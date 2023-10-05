import streamlit as st
import pandas as pd

from src.frontend.enums import Variables


class DataExtractorCombinePage:
    def __init__(self, canvas, handler):
        self.canvas = canvas
        self.handler = handler

    def show(self):
        with self.canvas.container():
            
            if 'tmp' not in st.session_state:
                # Get model outcomes from backend
                tmp = pd.DataFrame(self.handler.perform_data_extraction_clustering(
                st.session_state[Variables.DE_FINAL_CONFIG],
                st.session_state[Variables.SB_LOADED_DATAFRAME],
                st.session_state[Variables.DE_CLUSTER_DF],
            ))
                st.session_state['tmp'] = tmp
            else: 
                tmp = st.session_state['tmp']
            
            merge_dict = {}

            for e in range(len(st.session_state['tmp']["Cluster"])):
                value_to_replace = st.session_state['tmp']["Cluster"][e]
                with st.expander(label=f"Cluster #{e}", expanded=True if e == 0 else False):
                    col1AA, col2AA = st.columns([2, 1])
                    with col1AA:
                        values = st.multiselect(label=f"Current Values: ", options=st.session_state['tmp']["Values"][e],
                                                default=st.session_state['tmp']["Values"][e],
                                                key=f"multiselect_{e}")
                    with col2AA:
                        st.session_state['tmp']["Cluster"][e] = st.text_input(label="New Value: ",
                                                                              value=value_to_replace,
                                                                              key=f"text_input_{e}", )

                merge_dict[st.session_state['tmp']["Cluster"][e]] = values

            col1BBB, col2BBB, col3BBB, _ = st.columns([1, 1, 1, 1])
            with col2BBB:
                st.write("")
                st.write("")
                create_new_flag = st.checkbox(label="Create new column")
            with col3BBB:
                if create_new_flag:
                    new_col_name = st.text_input(label="New column name: ",
                                                 value=f"{st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]}_combined")
            with col1BBB:
                st.write("")
                st.write("")
                if st.button(label="Combine clusters"):
                    if create_new_flag:
                        st.session_state[Variables.SB_LOADED_DATAFRAME][new_col_name] = \
                        st.session_state[Variables.SB_LOADED_DATAFRAME][st.session_state[Variables.DE_FINAL_CONFIG][
                            Variables.DE_FINAL_CONFIG_COLUMN]].copy().astype(str)
                    for key, value in merge_dict.items():
                        for v in value:
                            if not create_new_flag:
                                st.session_state[Variables.SB_LOADED_DATAFRAME][
                                    st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]] = \
                                st.session_state[Variables.SB_LOADED_DATAFRAME][
                                    st.session_state[Variables.DE_FINAL_CONFIG][
                                        Variables.DE_FINAL_CONFIG_COLUMN]].replace(v, key)
                            else:
                                st.session_state[Variables.SB_LOADED_DATAFRAME][new_col_name] = \
                                st.session_state[Variables.SB_LOADED_DATAFRAME][new_col_name].replace(str(v), key)

                    st.session_state[Variables.GB_CURRENT_STATE] = None
                    st.experimental_rerun()