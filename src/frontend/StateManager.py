import json

import streamlit as st

from src.shared.Views.ColumnRuleView import ColumnRuleView
from src.shared.Configs.RuleFindingConfig import RuleFindingConfig
from src.frontend.enums.VarEnum import VarEnum
from src.frontend.Handler.IHandler import IHandler


class StateManager:

    def __init__(self) -> None:
        pass

    @staticmethod
    def turn_state_button_true(id):
        st.session_state[id] = True

    @staticmethod
    def turn_state_button_false(id):
        st.session_state[id] = False

    @staticmethod
    def restore_state(**kwargs) -> None:
        #file_string = kwargs["file_path"].split("\\")[1]
        file_string = kwargs["file_path"].split("/")[-1]
        content = kwargs["handler"].fetch_file_from_filepath(filepath=kwargs["file_path"])
        past_result_content_dict = json.loads(content)
        part_to_check_functionality = file_string.split('_')[0]
        part_to_check_state = file_string.split('_')[1]

        # SET CURRENT_SEQ TO CHOSEN ONE
        st.session_state[VarEnum.gb_CURRENT_SEQUENCE_NUMBER] = kwargs["chosen_seq"]

        # Grote If statement
        if part_to_check_functionality == "Rule-learning":
            if part_to_check_state == 'rules':
                st.session_state["gevonden_rules_dict"] = {k: ColumnRuleView.parse_from_json(v) for k,v in past_result_content_dict["result"].items()}
                t_dict = json.loads(past_result_content_dict["params"]["rule_finding_config_in_json"])
                for k,v in t_dict.items():
                    st.session_state[k] = v

                st.session_state["rule_finding_config"] = RuleFindingConfig(
                    rule_length=t_dict["rule_length"],
                    min_support=t_dict["min_support"],
                    lift=t_dict["lift"],
                    confidence=t_dict["confidence"],
                    filtering_string=t_dict["filtering_string"],
                    dropping_options=t_dict["dropping_options"],
                    binning_option=t_dict["binning_option"]
                    )
                st.session_state[VarEnum.gb_CURRENT_STATE] = "BekijkRules"

            if part_to_check_state == 'suggestions':
                # Zoek de rules-file die hieraan gelinkt is, om zo ook de
                st.session_state["suggesties_df"] = json.dumps(past_result_content_dict["result"])
                # FETCH PATH OF OTHER FILE FROM SESSION_MAP
                StateManager.restore_state(**{"handler" : kwargs["handler"], "file_path": st.session_state[VarEnum.gb_SESSION_MAP][kwargs["chosen_seq"]]["rules"], "chosen_seq": kwargs["chosen_seq"]})
                st.session_state[VarEnum.gb_CURRENT_STATE] = "BekijkSuggesties"
            return
        return

    @staticmethod
    def go_back_to_previous_in_flow() -> None:
        # RULE LEARNER
        current_state = st.session_state[VarEnum.gb_CURRENT_STATE]
        if current_state == "BekijkRules":
            st.session_state[VarEnum.gb_CURRENT_STATE] = None

            # Verschillende knoppen vanop de pagina terug False maken
            st.session_state["validate_own_rule_btn"] = False
            st.session_state["calculate_entropy_btn"] = False
            st.session_state["add_own_rule_btn"]  = False

            return
        if current_state == "BekijkSuggesties":
            st.session_state[VarEnum.gb_CURRENT_STATE] = "BekijkRules"
            return

        # ZINGG
        if current_state == VarEnum.st_DD_Labeling:
            st.session_state[VarEnum.gb_CURRENT_STATE] = None
            return

        if current_state == VarEnum.st_DD_Clustering:
            st.session_state[VarEnum.gb_CURRENT_STATE] = VarEnum.st_DD_Labeling
            return

    @staticmethod
    def initStateManagement(handler : IHandler):

        # LOADED DATAFRAME
        if VarEnum.sb_LOADED_DATAFRAME not in st.session_state:
            st.session_state[VarEnum.sb_LOADED_DATAFRAME] = None

        if VarEnum.sb_LOADED_DATAFRAME_HASH not in st.session_state:
            st.session_state[VarEnum.sb_LOADED_DATAFRAME_HASH] = None

        if VarEnum.sb_LOADED_DATAFRAME_separator not in st.session_state:
            st.session_state[VarEnum.sb_LOADED_DATAFRAME_separator] = None

        if VarEnum.sb_LOADED_DATAFRAME_NAME not in st.session_state:
            st.session_state[VarEnum.sb_LOADED_DATAFRAME_NAME] = None

        # DATASET DISPLAYER COMPONENT
        if VarEnum.ddc_FORCE_RELOAD_CACHE not in st.session_state:
            st.session_state[VarEnum.ddc_FORCE_RELOAD_CACHE] = False


        # SESSION
        if VarEnum.gb_SESSION_MAP not in st.session_state:
            if st.session_state[VarEnum.sb_LOADED_DATAFRAME] is not None:
                st.session_state[VarEnum.gb_SESSION_MAP] = handler.get_session_map(dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME].to_json())
                st.session_state[VarEnum.gb_CURRENT_SEQUENCE_NUMBER] = str(max([int(x) for x in st.session_state[VarEnum.gb_SESSION_MAP].keys()], default=0)+1)
            else:
                st.session_state[VarEnum.gb_SESSION_MAP] = None

        if VarEnum.gb_SESSION_ID not in st.session_state:
            st.session_state[VarEnum.gb_SESSION_ID] = None


        if VarEnum.dp_PANDAS_PROFILE not in st.session_state:
            st.session_state[VarEnum.dp_PANDAS_PROFILE] = None

        if VarEnum.dp_DATAPREP_PROFILE not in st.session_state:
            st.session_state[VarEnum.dp_DATAPREP_PROFILE] = None

        if VarEnum.gb_CURRENT_STATE not in st.session_state:
            st.session_state[VarEnum.gb_CURRENT_STATE] = None

        if VarEnum.sb_CURRENT_FUNCTIONALITY not in st.session_state:
            st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY] = None

        if VarEnum.sb_CURRENT_PROFILING not in st.session_state:
            st.session_state[VarEnum.sb_CURRENT_PROFILING] = None

        if 'currentRegel_LL' not in st.session_state:
            st.session_state['currentRegel_LL'] = None

        if 'currentRegel_RL' not in st.session_state:
            st.session_state['currentRegel_RL'] = None

        if 'ruleEdit' not in st.session_state:
            st.session_state["ruleEdit"] = {}

        if "ListActiveMergeDuplicates" not in  st.session_state:
            st.session_state["ListActiveMergeDuplicates"] = {}

        if "ListEditDuplicates" not in  st.session_state:
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
            st.session_state['dedupe_type_dict'] = {}

        if 'number_of_unsure' not in st.session_state:
            st.session_state['number_of_unsure'] = 0

        if "stashed_label_pair" not in st.session_state:
            st.session_state["stashed_label_pair"] = None

        if "record_pair" not in st.session_state:
            st.session_state["record_pair"] = None

        # CLEANER
        if VarEnum.dc_PIPELINE not in st.session_state:
            st.session_state[VarEnum.dc_PIPELINE] = {}

        if 'idx_of_structure_df' not in st.session_state:
            st.session_state['idx_of_structure_df'] = None

        if VarEnum.dc_CLEANED_COLUMN not in st.session_state:
            st.session_state[VarEnum.dc_CLEANED_COLUMN] = None

        if "list_of_fuzzy_cluster_view" not in st.session_state:
            st.session_state["list_of_fuzzy_cluster_view"] = []


    @staticmethod
    def reset_all_buttons():
        StateManager.turn_state_button_false("validate_own_rule_btn")
        StateManager.turn_state_button_false("add_own_rule_btn")
        StateManager.turn_state_button_false("select_all_suggestions_btn")
        StateManager.turn_state_button_false("select_all_rules_btn")
        StateManager.turn_state_button_false("calculate_entropy_btn")