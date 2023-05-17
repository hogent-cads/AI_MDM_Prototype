import streamlit as st

from src.frontend.RuleLearner.RuleLearnerSuggestionsPage import RuleLearnerSuggestionsPage
from src.frontend.RuleLearner.RuleLearnerInitPage import RuleLearnerInitPage
from src.frontend.RuleLearner.RuleLearnerSummaryRulesPage import (
    RuleLearnerSummaryRulesPage)
from src.frontend.Handler.IHandler import IHandler
from src.frontend.Cleaner.CleanerInitPage import CleanerInitPage
from src.frontend.Deduplication.InitPage import InitPage
from src.frontend.Deduplication.ClusterPage import (
    ZinggClusterRedirectPage, ZinggClusterPage)
from src.frontend.Profiler.ProfilerInitPage import ProfilerInitPage
from src.frontend.Extractor.DataExtractorInitPage import DataExtractorInitPage
from src.frontend.Deduplication.LabelPage import ZinggLabelPage
from src.frontend.enums.VarEnum import VarEnum


class Router:

    def __init__(self, handler:IHandler) -> None:
        self.handler = handler

    def route_data_extraction(self):
        canvas = st.empty()
                
        if st.session_state[VarEnum.gb_CURRENT_STATE] == None:
            DataExtractorInitPage(canvas=canvas, handler=self.handler).show()

    def route_data_profiling(self):
        canvas = st.empty()

        if st.session_state[VarEnum.gb_CURRENT_STATE] == None:
            ProfilerInitPage(canvas=canvas, handler=self.handler).show()

    def route_data_cleaning(self):
        canvas = st.empty()

        if st.session_state[VarEnum.gb_CURRENT_STATE] == None:
            CleanerInitPage(canvas=canvas, handler=self.handler).show()

    def route_rule_learning(self):
        canvas = st.empty()
                
        if st.session_state[VarEnum.gb_CURRENT_STATE] == None:
            RuleLearnerInitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE] == VarEnum.st_RL_Rules:
            RuleLearnerSummaryRulesPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE] == VarEnum.st_RL_Suggestions:
            RuleLearnerSuggestionsPage(canvas=canvas, handler=self.handler).show()

    def route_dedupe(self):
        canvas = st.empty()
                
        if st.session_state[VarEnum.gb_CURRENT_STATE] == None:
            InitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE] == VarEnum.st_DD_Labeling:
            ZinggLabelPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE] == VarEnum.st_DD_REDIRECT_Clustering:
            ZinggClusterRedirectPage(canvas=canvas, handler=self.handler).redirect_get_clusters()

        if st.session_state[VarEnum.gb_CURRENT_STATE] == VarEnum.st_DD_Clustering:
            ZinggClusterPage(canvas=canvas, handler=self.handler).show()
