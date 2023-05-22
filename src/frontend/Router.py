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
from src.frontend.enums import VarEnum


class Router:

    def __init__(self, handler:IHandler) -> None:
        self.handler = handler

    def route_data_extraction(self):
        canvas = st.empty()

        if st.session_state[VarEnum.GB_CURRENT_STATE] is None:
            DataExtractorInitPage(canvas=canvas, handler=self.handler).show()

    def route_data_profiling(self):
        canvas = st.empty()

        if st.session_state[VarEnum.GB_CURRENT_STATE] is None:
            ProfilerInitPage(canvas=canvas, handler=self.handler).show()

    def route_data_cleaning(self):
        canvas = st.empty()

        if st.session_state[VarEnum.GB_CURRENT_STATE] is None:
            CleanerInitPage(canvas=canvas, handler=self.handler).show()

    def route_rule_learning(self):
        canvas = st.empty()

        if st.session_state[VarEnum.GB_CURRENT_STATE] is None:
            RuleLearnerInitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.GB_CURRENT_STATE] == VarEnum.ST_RL_RULES:
            RuleLearnerSummaryRulesPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.GB_CURRENT_STATE] == VarEnum.ST_RL_SUGGESTIONS:
            RuleLearnerSuggestionsPage(canvas=canvas, handler=self.handler).show()

    def route_dedupe(self):
        canvas = st.empty()

        if st.session_state[VarEnum.GB_CURRENT_STATE] is None:
            InitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.GB_CURRENT_STATE] == VarEnum.ST_DD_LABELING:
            ZinggLabelPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.GB_CURRENT_STATE] == VarEnum.ST_DD_REDIRECT_CLUSTERING:
            ZinggClusterRedirectPage(canvas=canvas, handler=self.handler).redirect_get_clusters()

        if st.session_state[VarEnum.GB_CURRENT_STATE] == VarEnum.ST_DD_CLUSTERING:
            ZinggClusterPage(canvas=canvas, handler=self.handler).show()
