import json

import streamlit as st

from src.frontend.enums import Variables
from src.frontend.handler import IHandler
from src.shared.configs import RuleFindingConfig
from src.shared.views import ColumnRuleView


class StateManager:
    def __init__(self) -> None:
        pass

    @staticmethod
    def turn_state_button_true(button_id):
        st.session_state[button_id] = True

    @staticmethod
    def turn_state_button_false(button_id):
        st.session_state[button_id] = False

    @staticmethod
    def restore_state(**kwargs) -> None:
        # file_string = kwargs["file_path"].split("\\")[1]
        file_string = kwargs["file_path"].split("/")[-1]
        content = kwargs["handler"].fetch_file_from_filepath(
            filepath=kwargs["file_path"]
        )
        past_result_content_dict = json.loads(content)
        part_to_check_functionality = file_string.split("_")[0]
        part_to_check_state = file_string.split("_")[1]

        # SET CURRENT_SEQ TO CHOSEN ONE
        st.session_state[Variables.GB_CURRENT_SEQUENCE_NUMBER] = kwargs["chosen_seq"]

        # Grote If statement
        if part_to_check_functionality == "Rule-learning":
            if part_to_check_state == "rules":
                st.session_state["gevonden_rules_dict"] = {
                    k: ColumnRuleView.parse_from_json(v)
                    for k, v in past_result_content_dict["result"].items()
                }
                t_dict = json.loads(
                    past_result_content_dict["params"]["rule_finding_config_in_json"]
                )
                for k, v in t_dict.items():
                    st.session_state[k] = v

                st.session_state[Variables.RL_CONFIG] = RuleFindingConfig(
                    cols_to_use=t_dict["cols_to_use"],
                    rule_length=t_dict["rule_length"],
                    confidence=t_dict["confidence"],
                    speed=t_dict["speed"],
                    quality=t_dict["quality"],
                    abs_min_support=t_dict["abs_min_support"],
                    g3_threshold=t_dict["g3_threshold"],
                    fi_threshold=t_dict["fi_threshold"],
                    pyro=t_dict["pyro"],
                )
                st.session_state[Variables.GB_CURRENT_STATE] = "BekijkRules"

            if part_to_check_state == "suggestions":
                # Zoek de rules-file die hieraan gelinkt is, om zo ook de
                st.session_state["suggesties_df"] = json.dumps(
                    past_result_content_dict["result"]
                )
                # FETCH PATH OF OTHER FILE FROM SESSION_MAP
                StateManager.restore_state(
                    **{
                        "handler": kwargs["handler"],
                        "file_path": st.session_state[Variables.GB_SESSION_MAP][
                            kwargs["chosen_seq"]
                        ]["rules"],
                        "chosen_seq": kwargs["chosen_seq"],
                    }
                )
                st.session_state[Variables.GB_CURRENT_STATE] = "BekijkSuggesties"
            return
        return

    @staticmethod
    def go_back_to_previous_in_flow() -> None:
        # RULE LEARNER
        current_state = st.session_state[Variables.GB_CURRENT_STATE]
        if current_state == "BekijkRules":
            st.session_state[Variables.GB_CURRENT_STATE] = None

            # Verschillende knoppen vanop de pagina terug False maken
            st.session_state["validate_own_rule_btn"] = False
            st.session_state["calculate_entropy_btn"] = False
            st.session_state["add_own_rule_btn"] = False

            return
        if current_state == "BekijkSuggesties":
            st.session_state[Variables.GB_CURRENT_STATE] = "BekijkRules"
            return

        # ZINGG
        if current_state == Variables.ST_DD_LABELING:
            st.session_state[Variables.GB_CURRENT_STATE] = None
            return

        if current_state == Variables.ST_DD_CLUSTERING:
            st.session_state[Variables.GB_CURRENT_STATE] = Variables.ST_DD_LABELING
            return

        # Data Extractor
        if current_state == Variables.ST_DE_RESULTS:
            st.session_state[Variables.GB_CURRENT_STATE] = None
            return

        if current_state == Variables.ST_DE_COMBINE:
            st.session_state[Variables.GB_CURRENT_STATE] = Variables.ST_DE_RESULTS
            return

    @staticmethod
    def initStateManagement(handler: IHandler):
        # LOADED DATAFRAME
        if Variables.SB_LOADED_DATAFRAME not in st.session_state:
            st.session_state[Variables.SB_LOADED_DATAFRAME] = None

        if Variables.SB_LOADED_DATAFRAME_HASH not in st.session_state:
            st.session_state[Variables.SB_LOADED_DATAFRAME_HASH] = None

        if Variables.SB_LOADED_DATAFRAME_SEPARATOR not in st.session_state:
            st.session_state[Variables.SB_LOADED_DATAFRAME_SEPARATOR] = None

        if Variables.SB_LOADED_DATAFRAME_NAME not in st.session_state:
            st.session_state[Variables.SB_LOADED_DATAFRAME_NAME] = None

        # DATASET DISPLAYER COMPONENT
        if Variables.DDC_FORCE_RELOAD_CACHE not in st.session_state:
            st.session_state[Variables.DDC_FORCE_RELOAD_CACHE] = False

        # SESSION
        if Variables.GB_SESSION_MAP not in st.session_state:
            if st.session_state[Variables.SB_LOADED_DATAFRAME] is not None:
                st.session_state[Variables.GB_SESSION_MAP] = handler.get_session_map(
                    dataframe_in_json=st.session_state[
                        Variables.SB_LOADED_DATAFRAME
                    ].to_json()
                )
                st.session_state[Variables.GB_CURRENT_SEQUENCE_NUMBER] = str(
                    max(
                        [
                            int(x)
                            for x in st.session_state[Variables.GB_SESSION_MAP].keys()
                        ],
                        default=0,
                    )
                    + 1
                )
            else:
                st.session_state[Variables.GB_SESSION_MAP] = None

        if Variables.GB_SESSION_ID not in st.session_state:
            st.session_state[Variables.GB_SESSION_ID] = None

        if Variables.DP_PANDAS_PROFILE not in st.session_state:
            st.session_state[Variables.DP_PANDAS_PROFILE] = None

        if Variables.DP_DATAPREP_PROFILE not in st.session_state:
            st.session_state[Variables.DP_DATAPREP_PROFILE] = None

        if Variables.GB_CURRENT_STATE not in st.session_state:
            st.session_state[Variables.GB_CURRENT_STATE] = None

        if Variables.SB_CURRENT_FUNCTIONALITY not in st.session_state:
            st.session_state[Variables.SB_CURRENT_FUNCTIONALITY] = None

        if Variables.SB_CURRENT_PROFILING not in st.session_state:
            st.session_state[Variables.SB_CURRENT_PROFILING] = None

        if "currentRegel_LL" not in st.session_state:
            st.session_state["currentRegel_LL"] = None

        if "currentRegel_RL" not in st.session_state:
            st.session_state["currentRegel_RL"] = None

        if "ruleEdit" not in st.session_state:
            st.session_state["ruleEdit"] = {}

        if "ListActiveMergeDuplicates" not in st.session_state:
            st.session_state["ListActiveMergeDuplicates"] = {}

        if "ListEditDuplicates" not in st.session_state:
            st.session_state["ListEditDuplicates"] = {}

        if "AdviseerOpslaan" not in st.session_state:
            st.session_state["AdviseerOpslaan"] = False

        # BUTTONS

        if "validate_own_rule_btn" not in st.session_state:
            st.session_state["validate_own_rule_btn"] = False

        if "add_own_rule_btn" not in st.session_state:
            st.session_state["add_own_rule_btn"] = False

        if "select_all_rules_btn" not in st.session_state:
            st.session_state["select_all_rules_btn"] = False

        if "select_all_suggestions_btn" not in st.session_state:
            st.session_state["select_all_suggestions_btn"] = False

        if "calculate_entropy_btn" not in st.session_state:
            st.session_state["calculate_entropy_btn"] = False

        if "use_previous_label_btn" not in st.session_state:
            st.session_state["use_previous_label_btn"] = False

        # DEDUPE

        if "dedupe_type_dict" not in st.session_state:
            st.session_state["dedupe_type_dict"] = {}

        if "number_of_unsure" not in st.session_state:
            st.session_state["number_of_unsure"] = 0

        if "stashed_label_pair" not in st.session_state:
            st.session_state["stashed_label_pair"] = None

        if "record_pair" not in st.session_state:
            st.session_state["record_pair"] = None

        # CLEANER
        if Variables.DC_PIPELINE not in st.session_state:
            st.session_state[Variables.DC_PIPELINE] = {}

        if "idx_of_structure_df" not in st.session_state:
            st.session_state["idx_of_structure_df"] = None

        if Variables.DC_CLEANED_COLUMN not in st.session_state:
            st.session_state[Variables.DC_CLEANED_COLUMN] = None

        if "list_of_fuzzy_cluster_view" not in st.session_state:
            st.session_state["list_of_fuzzy_cluster_view"] = []

        # DATA EXTRACTOR
        if Variables.DE_SCORES not in st.session_state:
            st.session_state[Variables.DE_SCORES] = None

        if Variables.DE_STORED_CONFIG not in st.session_state:
            st.session_state[Variables.DE_STORED_CONFIG] = {}

    @staticmethod
    def reset_all_buttons():
        StateManager.turn_state_button_false("validate_own_rule_btn")
        StateManager.turn_state_button_false("add_own_rule_btn")
        StateManager.turn_state_button_false("select_all_suggestions_btn")
        StateManager.turn_state_button_false("select_all_rules_btn")
        StateManager.turn_state_button_false("calculate_entropy_btn")
