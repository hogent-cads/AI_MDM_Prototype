from typing import List, Set
import hashlib

import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid

from src.frontend.state_manager import StateManager
from src.frontend.handler import IHandler
from src.frontend.enums import Variables
import config as cfg


class RuleLearnerSuggestionsPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):
        with self.canvas.container():
            extra_grid_options = {
                "alwaysShowHorizontalScroll": True,
                "alwaysShowVerticalScroll": True,
                "pagination": True,
                "paginationPageSize": len(
                    st.session_state[Variables.SB_LOADED_DATAFRAME]
                ),
            }

            st.title("Rule Learning")
            df_with_predictions = pd.read_json(eval(st.session_state["suggesties_df"]))

            # Controleer of er wel suggesties gevonden zijn
            if df_with_predictions.shape[0] == 0:
                st.markdown("**There are no more suggestions**")
                return

            st.header("Suggestions for the selected rules:")
            df_with_predictions = df_with_predictions[
                df_with_predictions.columns.drop(
                    list(
                        df_with_predictions.filter(
                            regex="(__SCORE.*|__PREDICTION.*|__BEST_SCORE)"
                        )
                    )
                )
            ]

            # Order columns: __BEST_RULE and __BEST_PREDICTION at the front
            # TODO: this seems brittle, relies on the order of the columns in dataframe
            cols = df_with_predictions.columns.tolist()
            cols = cols[-2:] + cols[:-2]
            df_with_predictions = df_with_predictions[cols]

            suggestions_rows_selected = []
            list_of_df_idx = []

            gb1 = GridOptionsBuilder.from_dataframe(df_with_predictions)
            gb1.configure_grid_options(fit_columns_on_grid_load=True)
            gb1.configure_selection(
                "multiple",
                pre_select_all_rows=False,
                use_checkbox=True,
                groupSelectsChildren=True,
                groupSelectsFiltered=True,
                header_checkbox=True,
            )
            response_selection_suggestion_finder = AgGrid(
                df_with_predictions,
                height=350,
                editable=False,
                gridOptions=gb1.build() | extra_grid_options,
                data_return_mode="filtered_and_sorted",
                update_mode="selection_changed",
                theme="streamlit",
                enable_enterprise_modules=False,
            )

            (
                colb0,
                colb1,
                colb2,
            ) = st.columns([1, 1, 2])

            aangepaste_dataset = st.container()

            with colb0:
                apply_suggestions = st.button(
                    "Apply the selected suggestions", key="apply_suggestions"
                )
                # Maak tijdelijke dataframe aan, zodat wijzigingen niet meteen
                # de sidebar gaan beginnen aanpassen

                if apply_suggestions:
                    st.session_state["temp_dataframe"] = st.session_state[
                        Variables.SB_LOADED_DATAFRAME
                    ].copy()
                    suggestions_rows_selected = response_selection_suggestion_finder[
                        "selected_rows"
                    ]

                    list_of_df_idx = df_with_predictions.index

                    # TODO: Remove this 'old' code once we are satisfied with the 'new' code
                    # Start original code
                    # print(f"list_of_df_idx = {list_of_df_idx}")
                    # set_of_cols = set()
                    # # Is this correct? I don't think so.
                    # for idx, row in enumerate(suggestions_rows_selected):
                    #     index_of_to_change = list_of_df_idx[idx]
                    #     val_to_change = row["__BEST_PREDICTION"]
                    #     rs = row["__BEST_RULE"]
                    #     rss = rs.split(" => ")
                    #     col_to_change = rss[1]
                    #     set_of_cols.add(col_to_change)
                    #     for e in rss[0].split(","):
                    #         set_of_cols.add(e)
                    #     # Change value in temp_dataframe
                    #     st.session_state["temp_dataframe"].loc[
                    #         index_of_to_change, col_to_change
                    #     ] = val_to_change
                    #
                    # st.session_state[
                    #     "columns_affected_by_suggestion_application"
                    # ] = list(set_of_cols)
                    # End original code

                    # Start new code
                    indices_in_idx = [sel_row['_selectedRowNodeInfo']['nodeRowIndex']
                                      for sel_row in suggestions_rows_selected]
                    st.session_state["temp_dataframe"] = _apply_suggestions(
                        current_df=st.session_state["temp_dataframe"],
                        predictions_df=df_with_predictions,
                        indices_in_index=indices_in_idx)
                    st.session_state[
                        "columns_affected_by_suggestion_application"
                    ] = _compute_affected_columns(
                        predictions_df=df_with_predictions,
                        indices_in_index=indices_in_idx
                    )
                    # End new code


                    with aangepaste_dataset:
                        st.info(
                            'Changes have been applied to the dataset!' +
                            ' Press the "Recalculate rules" button to see what impact your' +
                            ' changes have on the rules.'
                        )
                        st.header("Modified dataset:")
                        rows_selected = []

                        # ?? What is the purpose of this code
                        for idx, row in enumerate(suggestions_rows_selected):
                            rows_selected.append(int(list_of_df_idx[idx]))

                        gb22 = GridOptionsBuilder.from_dataframe(
                            st.session_state["temp_dataframe"]
                        )
                        gb22.configure_side_bar()
                        # gb22.configure_selection('multiple', pre_selected_rows=rows_selected)
                        # gb22.configure_default_column(
                        #     groupable=True,
                        #     value=True,
                        #     enableRowGroup=True,
                        #     aggFunc="sum",
                        #     editable=False)
                        gridOptions = gb22.build()
                        _ = AgGrid(
                            st.session_state["temp_dataframe"],
                            gridOptions=gridOptions | extra_grid_options,
                            enable_enterprise_modules=True,
                            height=350,
                            key="aangepaste_dataset",
                        )

            with colb1:
                submitted = st.button("Recalculate rules")
                if submitted:
                    # Get the rule_finding_config from the session_state
                    rule_finding_config = st.session_state["rule_finding_config"]

                    json_rule_finding_config = rule_finding_config.to_json()

                    # recalculate unique storage id
                    # st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH] = f"{st.session_state[VarEnum.gb_SESSION_ID]}-{hashlib.md5(st.session_state['temp_dataframe'].to_json().encode('utf-8')).hexdigest()}"

                    st.session_state[Variables.SB_LOADED_DATAFRAME_HASH] = hashlib.md5(
                        st.session_state["temp_dataframe"].to_json().encode("utf-8")
                    ).hexdigest()

                    self.handler.recalculate_column_rules(
                        old_df_in_json=st.session_state[Variables.SB_LOADED_DATAFRAME][
                            st.session_state["cols_to_use"]
                        ].to_json(),
                        new_df_in_json=st.session_state["temp_dataframe"].to_json(),
                        rule_finding_config_in_json=json_rule_finding_config,
                        affected_columns=st.session_state[
                            "columns_affected_by_suggestion_application"
                        ],
                    )
                    # Reset columns_affected_by_suggestion_application
                    del st.session_state["columns_affected_by_suggestion_application"]

                    cfg.logger.debug("Recalculate rules done")

                    # Restore state van de aangemaakte file in de session_map
                    st.session_state[
                        Variables.GB_SESSION_MAP
                    ] = self.handler.get_session_map(
                        st.session_state["temp_dataframe"].to_json()
                    )
                    StateManager.restore_state(
                        **{
                            "handler": self.handler,
                            "file_path": st.session_state[Variables.GB_SESSION_MAP]["1"][
                                "rules"
                            ],
                            "chosen_seq": "1",
                        }
                    )

                    # Nieuwe dataframe, betekent sowieso dat current_session gelijk zal zijn aan 1:
                    st.session_state[Variables.SB_LOADED_DATAFRAME] = st.session_state[
                        "temp_dataframe"
                    ].copy()
                    st.session_state[Variables.GB_CURRENT_SEQUENCE_NUMBER] = 1

                    st.experimental_rerun()

            with colb2:
                # Download de temp_dataframe
                if "columns_affected_by_suggestion_application" in st.session_state:
                    st.download_button(
                        label="Download modified dataset",
                        data=st.session_state["temp_dataframe"]
                        .to_csv(index=False)
                        .encode("utf-8"),
                        file_name=f"new_{st.session_state[Variables.SB_LOADED_DATAFRAME_NAME]}",
                        mime="text/csv",
                    )


def _apply_suggestions(
        current_df: pd.DataFrame,
        predictions_df: pd.DataFrame,
        indices_in_index: List[int]
) -> pd.DataFrame:
    """
    current_df: the DataFrame where we are going to apply the suggestions to
    predictions_df: the DataFrame with the predictions.
                    We use the columns "__BEST_RULE" and "__BEST_PREDICTION"
    indices_in_index: list of integers that says which element from the index
                      of predictions_df to select.
                      This then determines the row to change in the current_df

    returns: a new dataframe with the same number of rows and columns as current_df
             but with the suggestions applied to it
    """
    # Start by making a defensive copy of the dataframe
    new_df = current_df.copy()

    for idx_in_idx in indices_in_index:
        idx = predictions_df.index[idx_in_idx]
        consequent = predictions_df.loc[idx, "__BEST_RULE"].split(" => ")[1]
        new_value = predictions_df.loc[idx, "__BEST_PREDICTION"]
        new_df.loc[idx, consequent] = new_value

    return new_df


def _compute_affected_columns(
    predictions_df: pd.DataFrame,
    indices_in_index: List[int]
) -> List[str]:
    """
    Determine the columns that participate in at least one applied rule.

    predictions_df: the DataFrame with the predictions.
                    We use the columns "__BEST_RULE"
    indices_in_index: list of integers that says which element from the index
                      of predictions_df to select.
                      This then determines the row to change in the current_df

    returns: a list of strings, where each string is the name of column
             participating in at least one rule
    """
    cols : Set[str] = set()
    for idx_in_idx in indices_in_index:
        idx = predictions_df.index[idx_in_idx]
        rule_str = predictions_df.loc[idx, "__BEST_RULE"]
        antecedents = rule_str.split(" => ")[0].split(",")
        cols.update(antecedents)
        consequent = rule_str.split(" => ")[1]
        cols.add(consequent)

    return list(cols)
