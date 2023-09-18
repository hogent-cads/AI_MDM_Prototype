import streamlit as st

from src.frontend.enums import Variables
from src.frontend.handler import IHandler
from src.frontend.pages.cleaning.cleaning_init import CleanerInitPage
from src.frontend.pages.deduplication.deduplication_clustering import (
    ZinggClusterRedirectPage, ZinggClusterPage)
from src.frontend.pages.deduplication.deduplication_init import InitPage
from src.frontend.pages.deduplication.deduplication_labeling import ZinggLabelPage
from src.frontend.pages.extraction.extraction_combine import DataExtractorCombinePage
from src.frontend.pages.extraction.extraction_init import DataExtractorInitPage
from src.frontend.pages.extraction.extraction_results import DataExtractorResultsPage
from src.frontend.pages.profiling.profiling_init import ProfilerInitPage
from src.frontend.pages.rule_learning.rule_learning_init import RuleLearnerInitPage
from src.frontend.pages.rule_learning.rule_learning_rules import (
    RuleLearnerSummaryRulesPage)
from src.frontend.pages.rule_learning.rule_learning_suggestions import RuleLearnerSuggestionsPage


class Router:

    def __init__(self, handler: IHandler) -> None:
        self.handler = handler

    def route_data_extraction(self):
        canvas = st.empty()

        if st.session_state[Variables.GB_CURRENT_STATE] is None:
            DataExtractorInitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[Variables.GB_CURRENT_STATE] == Variables.ST_DE_RESULTS:
            DataExtractorResultsPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[Variables.GB_CURRENT_STATE] == Variables.ST_DE_COMBINE:
            DataExtractorCombinePage(canvas=canvas, handler=self.handler).show()

    def route_data_profiling(self):
        canvas = st.empty()

        if st.session_state[Variables.GB_CURRENT_STATE] is None:
            ProfilerInitPage(canvas=canvas, handler=self.handler).show()

    def route_data_cleaning(self):
        canvas = st.empty()

        if st.session_state[Variables.GB_CURRENT_STATE] is None:
            CleanerInitPage(canvas=canvas, handler=self.handler).show()

    def route_rule_learning(self):
        canvas = st.empty()

        if st.session_state[Variables.GB_CURRENT_STATE] is None:
            RuleLearnerInitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[Variables.GB_CURRENT_STATE] == Variables.ST_RL_RULES:
            RuleLearnerSummaryRulesPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[Variables.GB_CURRENT_STATE] == Variables.ST_RL_SUGGESTIONS:
            RuleLearnerSuggestionsPage(canvas=canvas, handler=self.handler).show()

    def route_dedupe(self):
        canvas = st.empty()

        if st.session_state[Variables.GB_CURRENT_STATE] is None:
            InitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[Variables.GB_CURRENT_STATE] == Variables.ST_DD_LABELING:
            ZinggLabelPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[Variables.GB_CURRENT_STATE] == Variables.ST_DD_REDIRECT_CLUSTERING:
            ZinggClusterRedirectPage(canvas=canvas, handler=self.handler).redirect_get_clusters()

        if st.session_state[Variables.GB_CURRENT_STATE] == Variables.ST_DD_CLUSTERING:
            ZinggClusterPage(canvas=canvas, handler=self.handler).show()
