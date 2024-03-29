import pandas as pd
import streamlit as st
import extra_streamlit_components as stx
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, JsCode, ColumnsAutoSizeMode

from src.frontend.handler import IHandler
from src.frontend.enums import Variables
from src.shared.configs import RuleFindingConfig
from src.frontend.components.dataset_displayer import (
    DatasetDisplayerComponent,
)

def _create_js_code_for_specific_column(var):
    return JsCode(f"""
        function(params) {{
            if (params.value >= {var})   {{
                return {{ textAlign: 'center', background: 'red' }};
            }}
            else{{return {{ textAlign: 'center' }} }}
        }};
    """)


class RuleLearnerInitPage:

    @staticmethod
    @st.cache_data
    def _create_default_dropping_dict(d):
        return d

    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):
        with self.canvas.container():
            # # Default values:
            if Variables.RL_CONFIG not in st.session_state:
                default_rule_length = 3
                default_confidence = 0.95
                default_speed = 0.95
                default_quality = 4.0
                default_abs_min_support = 3
                default_g3_threshold = 0.9
                default_fi_threshold = 0.9
                default_pyro = False
            else:
                default_rule_length = st.session_state[
                    Variables.RL_CONFIG
                ].rule_length
                default_confidence = st.session_state[Variables.RL_CONFIG].confidence
                default_speed = st.session_state[Variables.RL_CONFIG].speed
                default_quality = st.session_state[Variables.RL_CONFIG].quality
                default_abs_min_support = st.session_state[
                    Variables.RL_CONFIG
                ].abs_min_support
                default_g3_threshold = st.session_state[Variables.RL_CONFIG].g3_threshold
                default_fi_threshold = st.session_state[Variables.RL_CONFIG].fi_threshold
                default_pyro = st.session_state[Variables.RL_CONFIG].pyro

            chosen_tab = stx.tab_bar(
                data=[
                    stx.TabBarItemData(id=1, title="Dataset", description=""),
                    stx.TabBarItemData(id=2, title="Rule learning", description=""),
                ],
                default=1,
            )

            if chosen_tab == "1":
                DatasetDisplayerComponent().show()

            if chosen_tab == "2":
                st.header("Column Selection Settings")
                col_selection_settings_exp = st.expander("Exclusion Settings", expanded=False)
                with col_selection_settings_exp:
                    if "cols_to_exclude" not in st.session_state:
                        st.session_state["cols_to_exclude"] = []
                        st.session_state["cols_to_use"] = st.session_state[
                            Variables.SB_LOADED_DATAFRAME
                        ].columns.tolist()

                    st.write("We advise to exclude the following columns, \
                             based on these filter thresholds:")
                    colA_1, colA_2, colA_3 = st.columns([1, 1, 1])
                    with colA_1:
                        percent_nan_threshold = st.slider(
                            "Ratio of non empty values:",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.5,
                            step=0.01,
                            key="slider_percent_nan_threshold")
                    with colA_2:
                        dominant_column_threshold = st.slider(
                            "Threshold to determine the dominance of a value in a column:",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.75,
                            step=0.01,
                            key="slider_dominant_column_threshold")
                    with colA_3:
                        key_column_threshold = st.slider(
                            "Threshold to determine if a column uniquely identifies rows:",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.95,
                            step=0.01,
                            key="slider_key_column_threshold")

                    selection_filter_dataframe = st.container()

                    with selection_filter_dataframe:
                        selection_to_drop = self.show_column_filtering(
                            dominant_column_threshold,
                            key_column_threshold,
                            percent_nan_threshold)

                    if len(selection_to_drop) > 0:
                        exclude_btn = st.button("Exclude selected columns")
                        if exclude_btn:
                            cols_to_drop = [x[Variables.RL_SETTING_GRID_COLUMN.value] for x in
                                            selection_to_drop]

                            st.session_state["cols_to_exclude"] = list(
                                set(st.session_state["cols_to_exclude"] + cols_to_drop))
                            st.session_state["cols_to_use"] = \
                                [x for x in st.session_state["cols_to_use"]
                                 if x not in st.session_state["cols_to_exclude"]]
                            st.experimental_rerun()

                    st.session_state["cols_to_exclude"] = st.multiselect(
                        label="Columns that are excluded for rule learning:",
                        options=st.session_state[Variables.SB_LOADED_DATAFRAME].columns,
                        default=st.session_state["cols_to_exclude"],
                    )

                st.header("Rule quality Settings")
                basic_settings_exp = st.expander("Basic Settings", expanded=True)
                with basic_settings_exp:

                    rl_algo_col1,rl_algo_col2, rl_algo_col3 = st.columns([1, 1, 1])
                    with rl_algo_col1:
                        st.session_state[Variables.RL_SETTING_ALGO] = st.selectbox(
                            "Choose a rule learning algorithm",
                            options=[Variables.RL_SETTING_ALGO_Pyro.value, Variables.RL_SETTING_ALGO_FPG_FD.value],
                            index=1,
                        )

                    if st.session_state[Variables.RL_SETTING_ALGO] == Variables.RL_SETTING_ALGO_FPG_FD.value:

                        with rl_algo_col2:
                            st.session_state["rule_length"] = st.number_input(
                                "Rule length:", value=default_rule_length, format="%d"
                            )

                        with rl_algo_col3:
                            st.session_state["speed"] = st.slider(
                                "Speed",
                                min_value=0.0,
                                max_value=1.0,
                                value=default_speed,
                            )

                    rl_opt_col1, rl_opt_col2= st.columns([1, 1])
                    with rl_opt_col1:
                        st.session_state["confidence"] = st.slider(
                            "Minimum confidence",
                            min_value=0.0,
                            max_value=1.0,
                            value=default_confidence,
                        )
                    with rl_opt_col2:
                        st.session_state["quality"] = st.slider(
                            "Quality",
                            min_value=0.0,
                            max_value=5.0,
                            value=default_quality,
                            step=0.05
                        )

                adv_settings_exp = st.expander("Advanced Settings")
                with adv_settings_exp:

                    if st.session_state[Variables.RL_SETTING_ALGO] == Variables.RL_SETTING_ALGO_FPG_FD.value:
                    	st.session_state["abs_min_support"] = st.number_input(
                        	"Minimum number of records for a mapping of a rule:",
                        	value=default_abs_min_support,
                        	format="%d"
                    	)

                    st.session_state["g3_threshold"] = st.slider(
                        "g3_threshold",
                        min_value=0.0,
                        max_value=1.0,
                        value=default_g3_threshold,
                    )

                    st.session_state["fi_threshold"] = st.slider(
                        "fi_threshold",
                        min_value=0.0,
                        max_value=1.0,
                        value=default_fi_threshold,
                    )

                if st.button("Analyse Data"):
                    rule_finding_config = RuleFindingConfig(
                        rule_length=st.session_state["rule_length"],
                        confidence=st.session_state["confidence"],
                        cols_to_use=list(
                            set(st.session_state[Variables.SB_LOADED_DATAFRAME].columns) -
                            set(st.session_state["cols_to_exclude"])),
                        speed=st.session_state["speed"],
                        quality=st.session_state["quality"],
                        abs_min_support=st.session_state["abs_min_support"],
                        g3_threshold=st.session_state["g3_threshold"],
                        fi_threshold=st.session_state["fi_threshold"],
                        pyro=True if (st.session_state[Variables.RL_SETTING_ALGO] == Variables.RL_SETTING_ALGO_Pyro.value) else False,
                    )
                    # Sla rule finding config op in de session_state
                    st.session_state[Variables.RL_CONFIG] = rule_finding_config
                    json_rule_finding_config = rule_finding_config.to_json()

                    # Set session_state attributes
                    st.session_state[
                        "gevonden_rules_dict"
                    ] = self.handler.get_column_rules(
                        dataframe_in_json=st.session_state[
                            Variables.SB_LOADED_DATAFRAME].to_json(),
                        rule_finding_config_in_json=json_rule_finding_config,
                        seq=st.session_state[Variables.GB_CURRENT_SEQUENCE_NUMBER],
                    )
                    st.session_state[Variables.GB_CURRENT_STATE] = "BekijkRules"
                    st.experimental_rerun()

    def show_column_filtering(
            self,
            dominant_column_threshold,
            key_column_threshold,
            percent_nan_threshold):
        # For each column calculate a couple of metrics
        # 1. Percentage of empty values in a column
        # 2. The dominance of a value in a column, by looking at the maximum of value counts
        # 3. Percentage of uniqueness, by looking at the distinct values divided by the
        #    total number of values
        list_of_dicts = []
        for col in st.session_state["cols_to_use"]:
            dict_to_append = {}
            # 1. Percentage of empty values in a column
            percent_nan_value = st.session_state[Variables.SB_LOADED_DATAFRAME][
                                    col].isna().sum() / len(
                st.session_state[Variables.SB_LOADED_DATAFRAME][col])

            # 2. The dominance of a value in a column, by looking at the maximum of value counts
            vc = st.session_state[Variables.SB_LOADED_DATAFRAME][col].value_counts(
                normalize=True)
            dominant_column_value = vc.max()

            # 3. Percentage of uniqueness, by looking at the distinct values divided by
            # the total number of values
            unique_values = st.session_state[Variables.SB_LOADED_DATAFRAME][col].nunique()
            key_column_value = unique_values / len(
                st.session_state[Variables.SB_LOADED_DATAFRAME][col])

            if percent_nan_threshold <= percent_nan_value \
                    or dominant_column_threshold <= dominant_column_value \
                    or key_column_threshold <= key_column_value:
                dict_to_append[Variables.RL_SETTING_GRID_COLUMN.value] = col
                dict_to_append[
                    Variables.RL_SETTING_GRID_PERCENT_NAN.value] = percent_nan_value
                dict_to_append[
                    Variables.RL_SETTING_GRID_DOMINANT_COLUMN.value] = dominant_column_value
                dict_to_append[Variables.RL_SETTING_GRID_KEY_COLUMN.value] = key_column_value
                list_of_dicts.append(dict_to_append)
        df_of_columns_to_exclude_for_rl = pd.DataFrame(list_of_dicts)

        if len(df_of_columns_to_exclude_for_rl) == 0:
            st.write("No further columns that don't comply with these thresholds!")
            return []
        # Create an AGGRID with default all selected
        percent_nan_js = _create_js_code_for_specific_column(percent_nan_threshold)
        dominant_column_js = _create_js_code_for_specific_column(dominant_column_threshold)
        key_column_js = _create_js_code_for_specific_column(key_column_threshold)

        gb = GridOptionsBuilder.from_dataframe(
            df_of_columns_to_exclude_for_rl
        )
        gb.configure_side_bar()
        gb.configure_default_column(editable=True)
        gb.configure_column(
            field=Variables.RL_SETTING_GRID_PERCENT_NAN.value,
            cellStyle=percent_nan_js,
            headerClass="")
        gb.configure_column(
            field=Variables.RL_SETTING_GRID_DOMINANT_COLUMN.value,
            cellStyle=dominant_column_js,
            headerClass="")
        gb.configure_column(
            field=Variables.RL_SETTING_GRID_KEY_COLUMN.value,
            cellStyle=key_column_js,
            headerClass="")
        gb.configure_selection(
            selection_mode="multiple",
            use_checkbox=True,
            pre_select_all_rows=True,
            header_checkbox=True)
        standard_grid_options = gb.build()
        extra_grid_options = {
            "alwaysShowHorizontalScroll": True,
            "alwaysShowVerticalScroll": True,
        }
        grid_options = standard_grid_options | extra_grid_options
        grid_response = AgGrid(
            df_of_columns_to_exclude_for_rl,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        ),
        return grid_response[0]['selected_rows']
