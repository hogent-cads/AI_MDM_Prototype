import os

import streamlit as st
from streamlit_pandas_profiling import st_profile_report
import extra_streamlit_components as stx
from dataprep.eda import create_report
from ydata_profiling import ProfileReport

from src.frontend.Handler.IHandler import IHandler
from src.frontend.enums.VarEnum import VarEnum as v
from src.frontend.enums.DialogEnum import DialogEnum as d
from src.frontend.DatasetDisplayer.DatasetDisplayerComponent import (
    DatasetDisplayerComponent)
import config as cfg


class ProfilerInitPage:

    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):
        chosen_tab = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Dataset", description=""),
            stx.TabBarItemData(id=2, title=d.sb_DATA_PROFILING_option_pandas, description=""),
            stx.TabBarItemData(id=3, title=d.sb_DATA_PROFILING_option_dataprep, description=""),
            ], default=1)

        if chosen_tab == "1":
            DatasetDisplayerComponent().show()

        if chosen_tab == "2":
            self._show_pandas_profiling()

        if chosen_tab == "3":
            self._show_dataprep_profiling()


    def _show_pandas_profiling(self):
        if st.session_state[v.dp_PANDAS_PROFILE] is None:
            generate_profiling = st.button("Generate Pandas Profiling Report")
            if generate_profiling:
                st.header('The Data Profiling report is getting generated. Please wait...')
                st.session_state[v.dp_PANDAS_PROFILE] = ProfileReport(st.session_state[v.sb_LOADED_DATAFRAME])
                st_profile_report(st.session_state[v.dp_PANDAS_PROFILE])
        else:
            st_profile_report(st.session_state[v.dp_PANDAS_PROFILE])

    def _show_dataprep_profiling(self):
        if st.session_state[v.dp_DATAPREP_PROFILE] is None:
            generate_profiling = st.button("Generate Dataprep Profiling Report")
            if generate_profiling:
                st.header('The Data Profiling report is getting generated. Please wait...')
                # Make path to directory to store the reports.
                # We assume that this directory already exists.
                # The url starts from WWW_ROOT, so we need to go up one level
                # in order to get rid of "aimdmtool" in the url
                with st.spinner('Generating profile report...'):
                    path = os.path.join(os.path.join(cfg.configuration["WWW_ROOT"], "reports"), f"{st.session_state[v.sb_LOADED_DATAFRAME_HASH]}.html")
                    report = create_report(st.session_state[v.sb_LOADED_DATAFRAME])
                    report.save(path)

                st.session_state[v.dp_DATAPREP_PROFILE] = os.path.join("..", "reports", f"{st.session_state[v.sb_LOADED_DATAFRAME_HASH]}.html")
                st.markdown(f'<a href="{st.session_state[v.dp_DATAPREP_PROFILE]}">Link to the report</a>', unsafe_allow_html=True)
        else:
            st.header('Click on the link below to view the report')
            st.markdown(f'<a href="{st.session_state[v.dp_DATAPREP_PROFILE]}">Link to the report</a>', unsafe_allow_html=True)