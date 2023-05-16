import pandas as pd
import streamlit as st
import uuid
import hashlib
import uuid
# KEEP NESTED LAYOUT!
import streamlit_nested_layout
from src.frontend.Handler.LocalHandler import LocalHandler
from src.frontend.Handler.RemoteHandler import RemoteHandler
from src.frontend.Router import Router
from src.frontend.StateManager import StateManager
from streamlit_javascript import st_javascript
import json
import config as cfg

import asyncio
import time

import streamlit.components.v1 as components
import websockets
import config as cfg

from src.frontend.enums.DialogEnum import DialogEnum as d
from src.frontend.enums.VarEnum import VarEnum as v


def getOrCreateUID():
    if st.session_state[v.gb_SESSION_ID] is None:
        st.session_state[v.gb_SESSION_ID] = str(uuid.uuid1())
    return st.session_state[v.gb_SESSION_ID]


# Generate a unique uid that gets embedded in components.html for frontend
# Both frontend and server connect to ws using the same uid
# server sends commands like localStorage_get_key, localStorage_set_key, localStorage_clear_key etc. to the WS server,
# which relays the commands to the other connected endpoint (the frontend), and back
def injectWebsocketCode(hostPort, uid):
    code = '<script>function connect() { console.log("in connect uid: ", "' + uid + '"); var ws = new WebSocket("' + hostPort + '/?uid=' + uid + '");' + """
  ws.onopen = function() {
    // subscribe to some channels
    // ws.send(JSON.stringify({ status: 'connected' }));
    console.log("onopen");
  };
  ws.onmessage = function(e) {
    console.log('Message:', e.data);
    var obj = JSON.parse(e.data);
    if (obj.cmd == 'localStorage_get_key') {
        var val = localStorage[obj.key] || '';
        ws.send(JSON.stringify({ status: 'success', val }));
        console.log('returning: ', val);
    } else if (obj.cmd == 'localStorage_set_key') {
        localStorage[obj.key] = obj.val;
        ws.send(JSON.stringify({ status: 'success' }));
        console.log('set: ', obj.key, obj.val);
    }
  };
  ws.onclose = function(e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
    setTimeout(function() {
      connect();
    }, 1000);
  };
  ws.onerror = function(err) {
    console.error('Socket encountered error: ', err.message, 'Closing socket');
    ws.close();
  };
}
connect();
</script>
        """
    components.html(code, height=0)
    time.sleep(1)       # Without sleep there are problems
    return WebsocketClient(hostPort, uid)


class WebsocketClient:
    def __init__(self, hostPort, uid):
        self.hostPort = hostPort
        self.uid = uid
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def sendCommand(self, value, waitForResponse=True):

        async def query(future):
            async with websockets.connect(self.hostPort + "/?uid=" + self.uid) as ws:
                await ws.send(value)
                if waitForResponse:
                    response = await ws.recv()
                    print('response: ', response)
                    future.set_result(response)
                else:
                    future.set_result('')

        future1 = asyncio.Future()
        self.loop.run_until_complete(query(future1))
        print('future1.result: ', future1.result())
        return future1.result()

    def getLocalStorageVal(self, key):
        result = self.sendCommand(json.dumps({ 'cmd': 'localStorage_get_key', 'key': key }))
        return json.loads(result)['val']

    def setLocalStorageVal(self, key, val):
        cfg.logger.debug(f"Going to set {key} with {val} in local storage")
        result = self.sendCommand(json.dumps({ 'cmd': 'localStorage_set_key', 'key': key, 'val': val }))
        return result
    

def _remove_speciale_chars_from_columns(df:pd.DataFrame):
    df.columns = df.columns.str.replace('[^a-zA-Z0-9]', '')
    return df

def _hash_dataframe(df):
    return f"{hashlib.md5(df.to_json().encode('utf-8')).hexdigest()}"

def _reload_dataframe(uploaded_file, handler):
    
    sess_id = st.session_state[v.gb_SESSION_ID]
    separator = st.session_state[v.sb_LOADED_DATAFRAME_separator]
    
    current_funct = st.session_state[v.sb_CURRENT_FUNCTIONALITY]
    current_profiling = st.session_state[v.sb_CURRENT_PROFILING]
    skip_file_reading = st.session_state[v.ddc_FORCE_RELOAD_CACHE]
    
    if skip_file_reading == True:
        loaded_dataframe = st.session_state[v.sb_LOADED_DATAFRAME]
        loaded_dataframe_name = st.session_state[v.sb_LOADED_DATAFRAME_NAME]
        loaded_dataframe_id = st.session_state[v.sb_LOADED_DATAFRAME_ID]
        
    else:
        # Buffer is gone when pd.read_csv is called, so we need to reset the buffer
        uploaded_file.seek(0)

    for key in st.session_state.keys():
        del st.session_state[key]

    if skip_file_reading == True:
        st.session_state[v.sb_LOADED_DATAFRAME] = loaded_dataframe
        st.session_state[v.sb_LOADED_DATAFRAME_NAME] = loaded_dataframe_name
        st.session_state[v.sb_LOADED_DATAFRAME_ID] = loaded_dataframe_id
    else:
        st.session_state[v.sb_LOADED_DATAFRAME] = _remove_speciale_chars_from_columns(pd.read_csv(uploaded_file, delimiter= separator if separator else ','))        
        st.session_state[v.sb_LOADED_DATAFRAME_NAME] = uploaded_file.name
        st.session_state[v.sb_LOADED_DATAFRAME_ID] = uploaded_file.id

    st.session_state[v.sb_LOADED_DATAFRAME_separator] = separator
    st.session_state[v.sb_LOADED_DATAFRAME_HASH] = _hash_dataframe(st.session_state[v.sb_LOADED_DATAFRAME])

    st.session_state[v.gb_SESSION_ID] = sess_id 
    st.session_state[v.sb_CURRENT_FUNCTIONALITY] = current_funct
    st.session_state[v.sb_CURRENT_PROFILING] = current_profiling
    
    StateManager.initStateManagement(handler)

def main():
    # Page Style:
    st.set_page_config(page_title=d.gb_PAGE_TITLE.value, layout = "wide") 
    with open("src/frontend/Resources/css/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Choose whether to acces domain locally or remotely
    if cfg.configuration['HANDLER_TYPE'] == d.sb_TYPE_HANDLER_option_REMOTE.value:
        handler = RemoteHandler(f"http://{cfg.configuration['remote_url']}:{cfg.configuration['remote_port']}")
    else:
        handler = LocalHandler()

    # StateManagement
    StateManager.initStateManagement(handler)
    if st.session_state[v.gb_CURRENT_STATE] is not None:
        st.sidebar.button(d.sb_PREVIOUS_STATE_button, on_click=StateManager.go_back_to_previous_in_flow)
    
    # Cookie Management
    if st.session_state[v.sb_LOADED_DATAFRAME] is None and (st.session_state[v.sb_LOADED_DATAFRAME_HASH] is None):
        if st.session_state[v.gb_SESSION_ID] is None:
            url = cfg.configuration[v.cfg_WEBSOCKET_SERVER_URL]
            conn = injectWebsocketCode(hostPort=url, uid=getOrCreateUID())
            ret = conn.getLocalStorageVal(key="st_mdm_uid")
            if not ret:               
                _ = conn.setLocalStorageVal(key="st_mdm_uid", val=st.session_state[v.gb_SESSION_ID])
            else:
                st.session_state[v.gb_SESSION_ID] = ret

    # if st.session_state[v.sb_LOADED_DATAFRAME] is not None:
    #     st.session_state[v.sb_LOADED_DATAFRAME_HASH] = _hash_dataframe(st.session_state[v.sb_LOADED_DATAFRAME])

    # Sidebar vullen met functionaliteit-mogelijkheden
    st.session_state[v.sb_CURRENT_FUNCTIONALITY] = st.sidebar.selectbox(
        d.sb_FUNCTIONALITY_selectbox,
        (d.sb_FUNCTIONALITY_option_DATA_PROFILING.value,
        d.sb_FUNCTIONALITY_option_DATA_CLEANING.value,
        d.sb_FUNCTIONALITY_option_DATA_EXTRACTION.value,
        d.sb_FUNCTIONALITY_option_DEDUPLICATION.value,
        d.sb_FUNCTIONALITY_option_RULE_LEARNING.value),
        index=3
    )

    # Sidebar vullen met file-upload knop
    uploaded_file = st.sidebar.file_uploader(d.sb_UPLOAD_DATASET, key="_uploaded_file_widget")

    # Sidebar vullen met optionele separator
    if uploaded_file:
        if v.sb_LOADED_DATAFRAME_ID not in st.session_state:
             _reload_dataframe(uploaded_file,handler)

        with st.sidebar.expander(d.sb_OPTIONAL_separator.value, expanded=False):
            st.write(d.sb_OPTIONAL_separator_DESCRIPTION.value)
            col_sep_left, col_sep_right = st.columns([1,1])
            with col_sep_left:
                st.session_state[v.sb_LOADED_DATAFRAME_separator] = st.text_input(d.sb_separator.value, value=',')
            with col_sep_right:
                st.write("")
                st.write("")
                flag_reload = st.button(d.sb_RELOAD_BUTTON, key="_reload_button")
                if flag_reload:
                    _reload_dataframe(uploaded_file,handler)
        
        if (st.session_state[v.sb_LOADED_DATAFRAME_ID] != uploaded_file.id) or st.session_state[v.ddc_FORCE_RELOAD_CACHE] == True:
            _reload_dataframe(uploaded_file, handler)

        # CALCULATE CURRENT SEQ IF NOT ALREADY PRESENT
        # if v.gb_CURRENT_SEQUENCE_NUMBER not in st.session_state:
        #     st.session_state[v.gb_CURRENT_SEQUENCE_NUMBER] = str(max([int(x) for x in st.session_state[v.gb_SESSION_MAP].keys()], default=0)+1)

        # CREATE BUTTONS FROM SESSION_MAP 
        button_container =  st.sidebar.expander(label=d.sb_PREVIOUS_RESULTS, expanded=False)
        if st.session_state[v.gb_SESSION_MAP] is not None:
            for seq,method_dict in st.session_state[v.gb_SESSION_MAP].items():
                button_container.write(seq)
                for method, file_name in method_dict.items():
                    button_container.write(method)
                    button_container.button("⏪ " + seq + file_name.split("/")[-1],  # file_name.split("\\")[1], 
                                            on_click=StateManager.restore_state,
                                            kwargs={"handler": handler,
                                                    "file_path": file_name,
                                                    "chosen_seq": seq})
            
        # Toevoegen van download knop:
        # st.sidebar.button('Download huidige dataset')
        st.sidebar.download_button(
                label=d.sb_DOWNLOAD_DATASET.value,
                data=st.session_state[v.sb_LOADED_DATAFRAME].to_csv(index=False).encode('utf-8'),
                file_name= f'new_{st.session_state[v.sb_LOADED_DATAFRAME_NAME]}',
                mime='text/csv',
            )

        # Aanmaken van Router object:
        router = Router(handler=handler)
        if st.session_state[v.sb_CURRENT_FUNCTIONALITY] == d.sb_FUNCTIONALITY_option_DATA_PROFILING.value:
            router.route_data_profiling()
        if st.session_state[v.sb_CURRENT_FUNCTIONALITY] == d.sb_FUNCTIONALITY_option_DATA_CLEANING.value:
            router.route_data_cleaning()
        if st.session_state[v.sb_CURRENT_FUNCTIONALITY] == d.sb_FUNCTIONALITY_option_DEDUPLICATION.value:
            router.route_dedupe()
        if st.session_state[v.sb_CURRENT_FUNCTIONALITY] == d.sb_FUNCTIONALITY_option_RULE_LEARNING.value:
            router.route_rule_learning()
        if st.session_state[v.sb_CURRENT_FUNCTIONALITY] == d.sb_FUNCTIONALITY_option_DATA_EXTRACTION.value:
            router.route_data_extraction()

if __name__ == "__main__":
        print("Starting Streamlit")
        main()
