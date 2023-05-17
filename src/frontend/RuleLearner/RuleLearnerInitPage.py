import streamlit as st
import extra_streamlit_components as stx

from src.frontend.Handler.IHandler import IHandler
from src.shared.Enums.FiltererEnum import FiltererEnum
from src.shared.Enums.BinningEnum import BinningEnum
from src.shared.Enums.DroppingEnum import DroppingEnum
from src.frontend.enums.VarEnum import VarEnum
from src.shared.Configs.RuleFindingConfig import RuleFindingConfig
from src.frontend.DatasetDisplayer.DatasetDisplayerComponent import (
    DatasetDisplayerComponent)


class RuleLearnerInitPage:

    def _create_total_binning_dict(_self, dict_to_show):
        st.session_state["binning_option"] = dict_to_show
        return st.session_state["binning_option"]

    def _create_total_dropping_dict(_self, dict_to_show):
        st.session_state["dropping_options"] = dict_to_show
        return st.session_state["dropping_options"]

    @st.cache_data
    def _create_default_dropping_dict(_self, d):
        return d

    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler


    def show(self):

        with self.canvas.container():

            # # Default values:
            if "rule_finding_config" not in st.session_state:
                default_rule_length = 3
                default_min_support = 0.0001
                default_lift = 1.0
                default_confidence = 0.95
                default_filtering_string = FiltererEnum.C_METRIC
                default_binning_option = {}
                default_dropping_options = {}
            else:
                default_rule_length = st.session_state["rule_finding_config"].rule_length
                default_min_support = st.session_state["rule_finding_config"].min_support
                default_lift = st.session_state["rule_finding_config"].lift
                default_confidence = st.session_state["rule_finding_config"].confidence
                default_filtering_string = st.session_state["rule_finding_config"].filtering_string
                default_binning_option = st.session_state["binning_option"]
                default_dropping_options = st.session_state["dropping_options"]

            preview_default_to_show = self._create_default_dropping_dict(default_dropping_options)
            if "dropping_options" in st.session_state:
                preview_total_to_show = self._create_total_dropping_dict(
                    st.session_state["dropping_options"])
            else:
                preview_total_to_show = self._create_total_dropping_dict({})
            if "binning_option" in st.session_state:
                preview_total_to_show_binning = self._create_total_binning_dict(
                    st.session_state["binning_option"])
            else:
                preview_total_to_show_binning = self._create_total_binning_dict({})
            # # END DEFAULTS

            chosen_tab = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Dataset", description=""),
            stx.TabBarItemData(id=2, title="Rule learning", description=""),
            # stx.TabBarItemData(id=3, title="Dropping options", description=""),
            # stx.TabBarItemData(id=4, title="Binning options", description=""),
            ], default=1)

            if chosen_tab == "1":
                DatasetDisplayerComponent().show()

            if chosen_tab == "2":
                st.session_state["colsToUse"] = st.multiselect(
                    label="Columns that you want to use for rule learning:",
                    options=st.session_state[VarEnum.SB_LOADED_DATAFRAME].columns,
                    default=st.session_state[VarEnum.SB_LOADED_DATAFRAME].columns.tolist()
                )

                st.session_state["rule_length"] = st.number_input(
                    'Rule length:',
                    value=default_rule_length,
                    format="%d")
                # st.session_state["min_support"] = st.slider(
                #     'Minimum support',
                #     min_value=0.0,
                #     max_value=1.0,
                #     step=0.0001,
                #     value=default_min_support)
                st.session_state["min_support"] = default_min_support
                # st.session_state["lift"] = st.slider(
                #     'Minimum lift',
                #     min_value=0.0,
                #     max_value=10.0,
                #     value=default_lift)
                st.session_state["lift"] = default_lift

                st.session_state["confidence"] = st.slider(
                    'Minimum confidence',
                    min_value=0.0,
                    max_value=1.0,
                    value=default_confidence)
                # st.session_state["filtering_string"] = st.selectbox(
                #     'Filtering Type:',
                #     [e.value for e in FiltererEnum],
                #     index=[e.value for e in FiltererEnum].index(default_filtering_string))
                st.session_state["filtering_string"] = default_filtering_string

                if st.button("Analyse Data"):
                    rule_finding_config = RuleFindingConfig(
                        rule_length=st.session_state["rule_length"],
                        min_support=st.session_state["min_support"],
                        lift=st.session_state["lift"],
                        confidence=st.session_state["confidence"],
                        filtering_string=st.session_state["filtering_string"],
                        # Tijdelijke vervanging voor de dropping_options
                        dropping_options=str(st.session_state["colsToUse"]),
                        binning_option=st.session_state["binning_option"]
                        )
                    # Sla rule finding config op in de session_state
                    st.session_state["rule_finding_config"] = rule_finding_config
                    json_rule_finding_config = rule_finding_config.to_json()

                    # Only keep the columns selected in the multiselect

                    # Set session_state attributes
                    st.session_state['gevonden_rules_dict'] = self.handler.get_column_rules(
                        dataframe_in_json=st.session_state[VarEnum.SB_LOADED_DATAFRAME][st.session_state["colsToUse"]].to_json(),
                        rule_finding_config_in_json=json_rule_finding_config,
                        seq=st.session_state[VarEnum.GB_CURRENT_SEQUENCE_NUMBER])
                    st.session_state[VarEnum.GB_CURRENT_STATE] = "BekijkRules"
                    st.experimental_rerun()


            if chosen_tab == "3":
                colA, colB, _, colC = st.columns([3, 4, 1, 8])
                with colB:
                    v = st.selectbox('Default Condition:', [e.value for e in DroppingEnum])
                    w = st.text_input("Default Value:")

                    colA_1, colB_1 = st.columns(2)
                    with colA_1:
                        button = st.button("Add/Change Default Condition")
                        if button:
                            if v and w:
                                preview_default_to_show[v] = w
                    with colB_1:
                        button2 = st.button("Remove Default Condition")
                        if button2:
                            if v and v in preview_default_to_show:
                                del preview_default_to_show[v]


                with colC:
                    st.subheader("Column-specific Dropping Options:")

                    kolom_specific = None
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        kolom_specific = st.selectbox(
                            'Column:',
                            [e for e in st.session_state[VarEnum.SB_LOADED_DATAFRAME].columns])
                    with col2:
                        vw_specific = st.selectbox(
                            'Condition:',
                            [e.value for e in DroppingEnum])
                    with col3:
                        value_specific = st.text_input("Value")

                    colC_1, colC_2, _ = st.columns([4, 4, 14])
                    with colC_1:
                        buttonC_1 = st.button("Add Condition")
                        if buttonC_1:
                            if kolom_specific and vw_specific and value_specific:
                                if kolom_specific not in preview_total_to_show:
                                    preview_total_to_show[kolom_specific] = {}
                                preview_total_to_show[kolom_specific][vw_specific] = value_specific
                    with colC_2:
                        buttonC_2 = st.button("Remove Condition")
                        if buttonC_2:
                            if vw_specific and kolom_specific:
                                del preview_total_to_show[kolom_specific][vw_specific]

                with colA:
                    st.subheader("Default Dropping Options:")
                    st.write(preview_default_to_show)

                    use_default = st.checkbox(
                        'Use default conditions',
                        value=True)
                    temp_dict = {key: preview_default_to_show.copy()
                                 for key in st.session_state[VarEnum.SB_LOADED_DATAFRAME].columns}
                    if use_default:
                        if preview_total_to_show is None:
                            preview_total_to_show = self._create_total_dropping_dict({})

                        for k, v in temp_dict.items():
                            for v1, v2 in v.items():
                                if k not in preview_total_to_show:
                                    preview_total_to_show[k] = {}
                                if v1 not in preview_total_to_show:
                                    preview_total_to_show[k][v1] = {}
                                preview_total_to_show[k][v1] = v2

                    else:
                        # Nu opnieuw de values uit temp_dict eruit gooien
                        for k, v in temp_dict.items():
                            for v1, v2 in v.items():
                                if k not in preview_total_to_show:
                                    preview_total_to_show[k] = {}
                                preview_total_to_show[k].pop(v1, None)

                    st.subheader("Options that will be applied:")
                    st.write(preview_total_to_show)

            if chosen_tab == "4":
                colA_binning, colB_binning = st.columns(2)
                with colA_binning:
                    st.subheader("Default Binning Option:")

                    default_binning_option = st.selectbox(
                        'Binning method:',
                        [e.value for e in BinningEnum], key="kolom_default_binning")
                    use_default_binning = st.checkbox(
                        'Use the default condition',
                        value=False,
                        key="checkbox_default_binning")
                    temp_dict_binning = {key: default_binning_option
                                         for key in st.session_state[VarEnum.SB_LOADED_DATAFRAME].columns}

                    if use_default_binning:
                        for k, v in temp_dict_binning.items():
                            preview_total_to_show_binning[k] = v
                    else:
                        for k, v in temp_dict_binning.items():
                            if k in preview_total_to_show_binning:
                                del preview_total_to_show_binning[k]

                with colB_binning:
                    st.subheader("Column-specific Binning Options:")
                    kolom_specific_binnig = None
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        kolom_specific_binnig = st.selectbox(
                            'Column:',
                            [e for e in st.session_state[VarEnum.SB_LOADED_DATAFRAME].columns],
                            key="Kolom_Binning")
                    with col2:
                        specific_binnig = st.selectbox(
                            'Binning method:',
                            [e.value for e in BinningEnum])

                    colC_1_binning, colC_2_binning, _ = st.columns([5, 7, 14])
                    with colC_1_binning:
                        buttonC_1_binning = st.button("Add Binning")
                        if buttonC_1_binning:
                            preview_total_to_show_binning[kolom_specific_binnig] = specific_binnig
                    with colC_2_binning:
                        buttonC_2_binning = st.button("Remove Binning")
                        if buttonC_2_binning:
                            if k in preview_total_to_show_binning:
                                del preview_total_to_show_binning[kolom_specific_binnig]

                st.subheader("Options that will be applied:")
                st.write(preview_total_to_show_binning)                