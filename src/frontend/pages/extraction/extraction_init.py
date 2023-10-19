import extra_streamlit_components as stx
import streamlit as st

from src.frontend.components.dataset_displayer import (
    DatasetDisplayerComponent,
)
from src.frontend.enums import Variables


class DataExtractorInitPage:
    def __init__(self, canvas, handler):
        self.canvas = canvas
        self.handler = handler

    def show(self):
        with self.canvas.container():
            chosen_tab = stx.tab_bar(
                data=[
                    stx.TabBarItemData(id=1, title="Dataset", description=""),
                    stx.TabBarItemData(id=2, title="Data Extraction", description=""),
                ],
                default=1,
            )
            if chosen_tab == "1":
                DatasetDisplayerComponent().show()

            if chosen_tab == "2":
                # DEFAULT CONFIG:
                if Variables.DE_CONFIG not in st.session_state:
                    dict_config = {
                        # Get first column of dataframe
                        "chosen_column": st.session_state[Variables.SB_LOADED_DATAFRAME].columns[0],
                        "chosen_type": "Categorical",
                        "chosen_algorithm": "HDBSCAN",
                        "range_iteration_lower": 5,
                        "range_iteration_upper": 15,
                        "number_of_scores": 5
                    }
                else:
                    dict_config = st.session_state[Variables.DE_CONFIG]

                st.subheader("What kind of extraction do you want to perform?")
                col_settings_1, col_settings_2, col_settings_3 = st.columns([1, 1, 1])
                with col_settings_1:
                    chosen_column = st.selectbox(label="Select column to extract information from: ",
                                                 options=st.session_state[Variables.SB_LOADED_DATAFRAME].columns,
                                                 index=0)

                with col_settings_2:
                    chosen_type = st.selectbox(label="Select type of extraction: ",
                                               options=["Categorical", "Numeric"])

                with col_settings_3:
                    chosen_algorithm = st.selectbox(label="Select algorithm: ",
                                                    options=["K-means", "HDBSCAN"])

                st.subheader("Select the range of iterations to perform the algorithm on: ")
                col_range_1, col_range_2, col_range_3 = st.columns([1, 1, 1])

                with col_range_1:
                    range_iteration_lower = st.number_input(label="Min. number of clusters:" if chosen_algorithm == "K-means" else "Min. cluster size",
                                                            min_value=2, max_value=len(
                            st.session_state[Variables.SB_LOADED_DATAFRAME]),
                                                            value=dict_config["range_iteration_lower"], step=1)

                with col_range_2:
                    range_iteration_upper = st.number_input(label="Max. number of clusters:" if chosen_algorithm == "K-means" else "Max. cluster size",
                                                            min_value=2, max_value=len(
                            st.session_state[Variables.SB_LOADED_DATAFRAME]),
                                                            value=dict_config["range_iteration_upper"], step=1)

                with col_range_3:
                    number_of_scores = st.slider(label="Number of iterations between min and max value: ", value=dict_config["number_of_scores"],
                                                 min_value=2, max_value=(range_iteration_upper - range_iteration_lower),
                                                 step=1)

                start_extraction_btn = st.button("Extract data from: " + chosen_column)

                if start_extraction_btn:
                    st.session_state[Variables.DE_CONFIG] = {"chosen_column": chosen_column,
                                                             "chosen_type": chosen_type,
                                                             "chosen_algorithm": chosen_algorithm,
                                                             "range_iteration_lower": range_iteration_lower,
                                                             "range_iteration_upper": range_iteration_upper,
                                                             "number_of_scores": number_of_scores}
                    st.session_state[Variables.GB_CURRENT_STATE] = Variables.ST_DE_RESULTS
                    st.experimental_rerun()
