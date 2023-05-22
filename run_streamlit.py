import json
import asyncio
import time
import uuid
import hashlib

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# KEEP NESTED LAYOUT!
import streamlit_nested_layout  # pylint: disable=unused-import
import websockets.client

from src.frontend.handler import LocalHandler, RemoteHandler
from src.frontend.router import Router
from src.frontend.state_manager import StateManager
from src.frontend.enums import DialogEnum as d, VarEnum as v
import config as cfg


def get_or_create_uid():
    if st.session_state[v.GB_SESSION_ID] is None:
        st.session_state[v.GB_SESSION_ID] = str(uuid.uuid1())
    return st.session_state[v.GB_SESSION_ID]


# Generate a unique uid that gets embedded in components.html for frontend Both frontend and
# server connect to ws using the same uid server sends commands like localStorage_get_key,
# localStorage_set_key, localStorage_clear_key etc. to the WS server, which relays the
# commands to the other connected endpoint (the frontend), and back
def inject_websocket_code(host_port, uid):
    code = (
        '<script>function connect() { console.log("in connect uid: ", "'
        + uid
        + '"); var ws = new WebSocket("'
        + host_port
        + "/?uid="
        + uid
        + '");'
        + """
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
    )
    components.html(code, height=0)
    time.sleep(1)  # Without sleep there are problems
    return WebsocketClient(host_port, uid)


class WebsocketClient:
    def __init__(self, host_port, uid):
        self.host_port = host_port
        self.uid = uid
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def send_command(self, value, wait_for_response=True):
        async def query(future):
            async with websockets.client.connect(self.host_port + "/?uid=" + self.uid) as ws:
                await ws.send(value)
                if wait_for_response:
                    response = await ws.recv()
                    print("response: ", response)
                    future.set_result(response)
                else:
                    future.set_result("")

        future1 = asyncio.Future()
        self.loop.run_until_complete(query(future1))
        print("future1.result: ", future1.result())
        return future1.result()

    def get_local_storage_val(self, key):
        result = self.send_command(
            json.dumps({"cmd": "localStorage_get_key", "key": key})
        )
        return json.loads(result)["val"]

    def set_local_storage_val(self, key, val):
        cfg.logger.debug("Going to set %s with %s in local storage", key, val)
        result = self.send_command(
            json.dumps({"cmd": "localStorage_set_key", "key": key, "val": val})
        )
        return result


def _remove_speciale_chars_from_columns(df: pd.DataFrame):
    df.columns = df.columns.str.replace("[^a-zA-Z0-9]", "")
    return df


def _hash_dataframe(df):
    return f"{hashlib.md5(df.to_json().encode('utf-8')).hexdigest()}"


def _reload_dataframe(uploaded_file, handler):
    sess_id = st.session_state[v.GB_SESSION_ID]
    separator = st.session_state[v.SB_LOADED_DATAFRAME_SEPARATOR]

    current_funct = st.session_state[v.SB_CURRENT_FUNCTIONALITY]
    current_profiling = st.session_state[v.SB_CURRENT_PROFILING]
    skip_file_reading = st.session_state[v.DDC_FORCE_RELOAD_CACHE]

    if skip_file_reading:
        loaded_dataframe = st.session_state[v.SB_LOADED_DATAFRAME]
        loaded_dataframe_name = st.session_state[v.SB_LOADED_DATAFRAME_NAME]
        loaded_dataframe_id = st.session_state[v.SB_LOADED_DATAFRAME_ID]

    else:
        # Buffer is gone when pd.read_csv is called, so we need to reset the buffer
        uploaded_file.seek(0)

    for key in st.session_state.keys():
        del st.session_state[key]

    if skip_file_reading:
        st.session_state[v.SB_LOADED_DATAFRAME] = loaded_dataframe
        st.session_state[v.SB_LOADED_DATAFRAME_NAME] = loaded_dataframe_name
        st.session_state[v.SB_LOADED_DATAFRAME_ID] = loaded_dataframe_id
    else:
        st.session_state[v.SB_LOADED_DATAFRAME] = _remove_speciale_chars_from_columns(
            pd.read_csv(uploaded_file, delimiter=separator if separator else ",")
        )
        st.session_state[v.SB_LOADED_DATAFRAME_NAME] = uploaded_file.name
        st.session_state[v.SB_LOADED_DATAFRAME_ID] = uploaded_file.id

    st.session_state[v.SB_LOADED_DATAFRAME_SEPARATOR] = separator
    st.session_state[v.SB_LOADED_DATAFRAME_HASH] = _hash_dataframe(
        st.session_state[v.SB_LOADED_DATAFRAME]
    )

    st.session_state[v.GB_SESSION_ID] = sess_id
    st.session_state[v.SB_CURRENT_FUNCTIONALITY] = current_funct
    st.session_state[v.SB_CURRENT_PROFILING] = current_profiling

    StateManager.initStateManagement(handler)


def main():
    # Page Style:
    st.set_page_config(page_title=d.GB_PAGE_TITLE.value, layout="wide")
    with open("src/frontend/resources/css/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Choose whether to access domain locally or remotely
    if cfg.configuration["HANDLER_TYPE"] == d.SB_TYPE_HANDLER_OPTION_REMOTE.value:
        handler = RemoteHandler(
            f"http://{cfg.configuration['remote_url']}:{cfg.configuration['remote_port']}"
        )
    else:
        handler = LocalHandler()

    # StateManagement
    StateManager.initStateManagement(handler)
    if st.session_state[v.GB_CURRENT_STATE] is not None:
        st.sidebar.button(
            d.SB_PREVIOUS_STATE_BUTTON,
            on_click=StateManager.go_back_to_previous_in_flow,
        )

    # Cookie Management
    if st.session_state[v.SB_LOADED_DATAFRAME] is None and (
        st.session_state[v.SB_LOADED_DATAFRAME_HASH] is None
    ):
        if st.session_state[v.GB_SESSION_ID] is None:
            url = cfg.configuration[v.CFG_WEBSOCKET_SERVER_URL]
            conn = inject_websocket_code(host_port=url, uid=get_or_create_uid())
            ret = conn.get_local_storage_val(key="st_mdm_uid")
            if not ret:
                _ = conn.set_local_storage_val(
                    key="st_mdm_uid", val=st.session_state[v.GB_SESSION_ID]
                )
            else:
                st.session_state[v.GB_SESSION_ID] = ret

    # if st.session_state[v.sb_LOADED_DATAFRAME] is not None:
    #     st.session_state[v.sb_LOADED_DATAFRAME_HASH] = \
    #        _hash_dataframe(st.session_state[v.sb_LOADED_DATAFRAME])

    # Sidebar vullen met functionaliteit-mogelijkheden
    st.session_state[v.SB_CURRENT_FUNCTIONALITY] = st.sidebar.selectbox(
        d.SB_FUNCTIONALITY_SELECTBOX,
        (
            d.SB_FUNCTIONALITY_OPTION_DATA_PROFILING.value,
            d.SB_FUNCTIONALITY_OPTION_DATA_CLEANING.value,
            d.SB_FUNCTIONALITY_OPTION_DATA_EXTRACTION.value,
            d.SB_FUNCTIONALITY_OPTION_DEDUPLICATION.value,
            d.SB_FUNCTIONALITY_OPTION_RULE_LEARNING.value,
        ),
        index=3,
    )

    # Sidebar vullen met file-upload knop
    uploaded_file = st.sidebar.file_uploader(
        d.SB_UPLOAD_DATASET, key="_uploaded_file_widget"
    )

    # Sidebar vullen met optionele separator
    if uploaded_file:
        if v.SB_LOADED_DATAFRAME_ID not in st.session_state:
            _reload_dataframe(uploaded_file, handler)

        with st.sidebar.expander(d.SB_OPTIONAL_SEPARATOR.value, expanded=False):
            st.write(d.SB_OPTIONAL_SEPARATOR_DESCRIPTION.value)
            col_sep_left, col_sep_right = st.columns([1, 1])
            with col_sep_left:
                st.session_state[v.SB_LOADED_DATAFRAME_SEPARATOR] = st.text_input(
                    d.SB_SEPARATOR.value, value=","
                )
            with col_sep_right:
                st.write("")
                st.write("")
                flag_reload = st.button(d.SB_RELOAD_BUTTON, key="_reload_button")
                if flag_reload:
                    _reload_dataframe(uploaded_file, handler)

        if (
            st.session_state[v.SB_LOADED_DATAFRAME_ID] != uploaded_file.id
        ) or st.session_state[v.DDC_FORCE_RELOAD_CACHE]:
            _reload_dataframe(uploaded_file, handler)

        # CALCULATE CURRENT SEQ IF NOT ALREADY PRESENT
        # if v.gb_CURRENT_SEQUENCE_NUMBER not in st.session_state:
        #     st.session_state[v.gb_CURRENT_SEQUENCE_NUMBER] = \
        #       str(max([int(x) for x in st.session_state[v.gb_SESSION_MAP].keys()], default=0)+1)

        # CREATE BUTTONS FROM SESSION_MAP
        button_container = st.sidebar.expander(
            label=d.SB_PREVIOUS_RESULTS, expanded=False
        )
        if st.session_state[v.GB_SESSION_MAP] is not None:
            for seq, method_dict in st.session_state[v.GB_SESSION_MAP].items():
                button_container.write(seq)
                for method, file_name in method_dict.items():
                    button_container.write(method)
                    button_container.button(
                        "⏪ "
                        + seq
                        + file_name.split("/")[-1],  # file_name.split("\\")[1],
                        on_click=StateManager.restore_state,
                        kwargs={
                            "handler": handler,
                            "file_path": file_name,
                            "chosen_seq": seq,
                        },
                    )

        # Toevoegen van download knop:
        # st.sidebar.button('Download huidige dataset')
        st.sidebar.download_button(
            label=d.SB_DOWNLOAD_DATASET.value,
            data=st.session_state[v.SB_LOADED_DATAFRAME]
            .to_csv(index=False)
            .encode("utf-8"),
            file_name=f"new_{st.session_state[v.SB_LOADED_DATAFRAME_NAME]}",
            mime="text/csv",
        )

        # Aanmaken van Router object:
        router = Router(handler=handler)
        if (
            st.session_state[v.SB_CURRENT_FUNCTIONALITY]
            == d.SB_FUNCTIONALITY_OPTION_DATA_PROFILING.value
        ):
            router.route_data_profiling()
        if (
            st.session_state[v.SB_CURRENT_FUNCTIONALITY]
            == d.SB_FUNCTIONALITY_OPTION_DATA_CLEANING.value
        ):
            router.route_data_cleaning()
        if (
            st.session_state[v.SB_CURRENT_FUNCTIONALITY]
            == d.SB_FUNCTIONALITY_OPTION_DEDUPLICATION.value
        ):
            router.route_dedupe()
        if (
            st.session_state[v.SB_CURRENT_FUNCTIONALITY]
            == d.SB_FUNCTIONALITY_OPTION_RULE_LEARNING.value
        ):
            router.route_rule_learning()
        if (
            st.session_state[v.SB_CURRENT_FUNCTIONALITY]
            == d.SB_FUNCTIONALITY_OPTION_DATA_EXTRACTION.value
        ):
            router.route_data_extraction()


if __name__ == "__main__":
    print("Starting Streamlit")
    main()
