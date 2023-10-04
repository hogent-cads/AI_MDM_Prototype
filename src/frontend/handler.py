import json
from abc import ABC, abstractmethod

import requests
import streamlit as st

from src.backend.DomainController import DomainController
from src.frontend.enums import Variables
from src.shared.views import ColumnRuleView


class IHandler(ABC):
    # RULE LEARNING
    @abstractmethod
    def get_column_rules(
        self, dataframe_in_json, rule_finding_config_in_json, seq
    ) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_column_rules_from_strings(self, dataframe_in_json, rule_string):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_suggestions_given_dataframe_and_column_rules(
        self, dataframe_in_json, list_of_rule_string_in_json, seq
    ):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def fetch_file_from_filepath(self, filepath: str):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_session_map(self, dataframe_in_json):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def recalculate_column_rules(
        self,
        old_df_in_json,
        new_df_in_json,
        rule_finding_config_in_json,
        affected_columns,
    ):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def prepare_zingg(self, dedupe_type_dict, dedupe_data) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def zingg_clear(self) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def run_zingg_phase(self, phase) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def zingg_unmarked_pairs(self) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def zingg_mark_pairs(self, marked_df) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def zingg_get_stats(self) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def zingg_get_clusters(self) -> json:
        raise Exception("Not implemented Exception")

    # DATA CLEANING
    @abstractmethod
    def clean_dataframe_dataprep(self, dataframe_in_json, custom_pipeline) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def fuzzy_match_dataprep(
        self, dataframe_in_json, col, cluster_method, df_name, ngram, radius, block_size
    ) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def structure_detection(self, series_in_json, exception_chars, compress) -> json:
        raise Exception("Not implemented Exception")
    
    @abstractmethod
    def add_rule_to_local_storage(self,
            dataframe_in_json,
            new_rule,
            rule_finding_config_in_json,
            seq)-> json:
        raise Exception("Not implemented Exception")
    
    @abstractmethod
    def calculate_data_extraction_evaluation_scores(
            self, config_dict, df_chosen_column) -> json:
        raise Exception("Not implemented Exception")
    
    @abstractmethod
    def perform_data_extraction_clustering(
            self, config_dict="", original_df="", df_to_cluster="") -> json:
        raise Exception("Not implemented Exception")


class LocalHandler(IHandler):
    def __init__(self) -> None:
        self.dc = DomainController()

    def get_column_rules(
        self, dataframe_in_json, rule_finding_config_in_json, seq
    ):
        return {
            k: ColumnRuleView.parse_from_json(v)
            for (k, v) in json.loads(
                self.dc.get_all_column_rules_from_df_and_config(
                    dataframe_in_json, rule_finding_config_in_json, seq
                )
            ).items()
        }

    def get_column_rules_from_strings(self, dataframe_in_json, rule_string):
        return ColumnRuleView.parse_from_json(
            self.dc.get_column_rules_from_strings(
                dataframe_in_json=dataframe_in_json, list_of_rule_string=[rule_string]
            )
        )

    def get_suggestions_given_dataframe_and_column_rules(
        self, dataframe_in_json, list_of_rule_string_in_json, seq
    ):
        return self.dc.get_suggestions_given_dataframe_and_column_rules(
            dataframe_in_json=dataframe_in_json,
            list_of_rule_string_in_json=list_of_rule_string_in_json,
            seq=seq,
        )

    def fetch_file_from_filepath(self, filepath: str):
        return self.dc.fetch_file_from_filepath(filepath=filepath)

    def get_session_map(self, dataframe_in_json):
        return self.dc.get_session_map(dataframe_in_json=dataframe_in_json)

    def recalculate_column_rules(
        self,
        old_df_in_json,
        new_df_in_json,
        rule_finding_config_in_json,
        affected_columns,
    ):
        return self.dc.recalculate_column_rules(
            old_df_in_json=old_df_in_json,
            new_df_in_json=new_df_in_json,
            rule_finding_config_in_json=rule_finding_config_in_json,
            affected_columns=json.dumps(affected_columns),
        )

    def add_rule_to_local_storage(self,
            dataframe_in_json,
            new_rule,
            rule_finding_config_in_json,
            seq)-> json:
        return self.dc.add_rule_to_local_storage(
            dataframe_in_json=dataframe_in_json,
            new_rule=new_rule,
            rule_finding_config_in_json=rule_finding_config_in_json,
            seq=seq
        )

    # ZINGG
    def prepare_zingg(self, dedupe_type_dict, dedupe_data) -> json:
        return self.dc.prepare_zingg(dedupe_type_dict, dedupe_data)

    def zingg_clear(self) -> json:
        return self.dc.zingg_clear()

    def run_zingg_phase(self, phase) -> json:
        return self.dc.run_zingg_phase(phase)

    def zingg_unmarked_pairs(self) -> json:
        return self.dc.zingg_unmarked_pairs()

    def zingg_mark_pairs(self, marked_df) -> json:
        return self.dc.zingg_mark_pairs(marked_df)

    def zingg_get_stats(self) -> json:
        return self.dc.zingg_get_stats()

    def zingg_get_clusters(self) -> json:
        return self.dc.zingg_get_clusters()

    # DATA CLEANING
    def clean_dataframe_dataprep(self, dataframe_in_json, custom_pipeline) -> json:
        return self.dc.clean_dataframe_dataprep(
            dataframe_in_json=dataframe_in_json, custom_pipeline=custom_pipeline
        )

    def fuzzy_match_dataprep(
        self, dataframe_in_json, col, cluster_method, df_name, ngram, radius, block_size
    ) -> json:
        return self.dc.fuzzy_match_dataprep(
            dataframe_in_json=dataframe_in_json,
            col=col,
            df_name=df_name,
            ngram=ngram,
            radius=radius,
            block_size=block_size,
        )

    def structure_detection(self, series_in_json, exception_chars, compress) -> json:
        return self.dc.structure_detection(
            series_in_json=series_in_json,
            exception_chars=exception_chars,
            compress=compress,
        )
    
    def calculate_data_extraction_evaluation_scores(
            self, config_dict, df_chosen_column) -> json:
        return self.dc.calculate_data_extraction_evaluation_scores(
            config_dict=config_dict,
            df_chosen_column=df_chosen_column
        )
    
    def perform_data_extraction_clustering(
            self, config_dict="", original_df="", df_to_cluster="") -> json:
        return self.dc.perform_data_extraction_clustering(
            config_dict=config_dict,
            original_df=original_df,
            df_to_cluster=df_to_cluster
        )

class RemoteHandler(IHandler):
    def __init__(self, connection_string) -> None:
        self.connection_string = connection_string

    def get_column_rules(
        self, dataframe_in_json, rule_finding_config_in_json, seq
    ):
        data = {"dataframe_in_json": dataframe_in_json, "rule_finding_config_in_json": rule_finding_config_in_json,
                "seq": seq}

        return {
            k: ColumnRuleView.parse_from_json(v)
            for (k, v) in requests.post(
                f"{self.connection_string}/get_all_column_rules_from_df_and_config",
                cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
                data=json.dumps(data),
            )
            .json()
            .items()
        }

    def get_column_rules_from_strings(self, dataframe_in_json, rule_string):
        data = {"dataframe_in_json": dataframe_in_json, "list_of_rule_string": [rule_string]}
        return ColumnRuleView.parse_from_json(
                requests.post(
                    f"{self.connection_string}/get_column_rules_from_strings",
                    data=json.dumps(data),
                ).json()[rule_string]
        )

    def get_suggestions_given_dataframe_and_column_rules(
        self, dataframe_in_json, list_of_rule_string_in_json, seq
    ):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["list_of_rule_string_in_json"] = list_of_rule_string_in_json
        data["seq"] = seq
        return json.dumps(
            requests.post(
                f"{self.connection_string}/get_suggestions_given_dataframe_and_column_rules",
                cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
                data=json.dumps(data),
            ).json()
        )

    def fetch_file_from_filepath(self, filepath: str):
        data = {}
        data["filepath"] = filepath
        return json.dumps(
            requests.post(
                f"{self.connection_string}/fetch_file_from_filepath",
                data=json.dumps(data),
            ).json()
        )

    def get_session_map(self, dataframe_in_json):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        return requests.post(
            f"{self.connection_string}/get_session_map",
            cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
            data=json.dumps(data),
        ).json()

    def recalculate_column_rules(
        self,
        old_df_in_json,
        new_df_in_json,
        rule_finding_config_in_json,
        affected_columns,
    ) -> None:
        data = {}
        data["old_dataframe_in_json"] = old_df_in_json
        data["new_dataframe_in_json"] = new_df_in_json
        data["rule_finding_config_in_json"] = rule_finding_config_in_json
        data["affected_columns"] = json.dumps(affected_columns)

        requests.post(
            f"{self.connection_string}/recalculate_column_rules",
            cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
            data=json.dumps(data),
        )

    def add_rule_to_local_storage(self,
            dataframe_in_json,
            new_rule,
            rule_finding_config_in_json,
            seq)-> json:
            data = {}
            data["dataframe_in_json"] = dataframe_in_json
            data["new_rule"] = new_rule
            data["rule_finding_config_in_json"] = rule_finding_config_in_json
            data["seq"] = seq
            
            requests.post(
                f"{self.connection_string}/add_rule_to_local_storage",
                cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
                data=json.dumps(data),
            )

    # DEDUPE
    def create_deduper_object(self, dedupe_type_dict, dedupe_data) -> json:
        data = {}
        data["dedupe_type_dict"] = dedupe_type_dict
        data["dedupe_data"] = dedupe_data
        requests.post(
            f"{self.connection_string}/create_deduper_object",
            cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
            data=json.dumps(data),
        )

    def dedupe_next_pair(self) -> json:
        return requests.get(
            f"{self.connection_string}/dedupe_next_pair",
            cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
        ).json()

    def dedupe_mark_pair(self, labeled_pair) -> json:
        data = {}
        data["labeled_pair"] = labeled_pair
        temp_data = json.dumps(data)
        requests.post(
            f"{self.connection_string}/dedupe_mark_pair",
            cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
            data=temp_data,
        )

    def dedupe_get_stats(self) -> json:
        return requests.get(
            f"{self.connection_string}/dedupe_get_stats",
            cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
        ).json()

    def dedupe_train(self):
        data = {}
        requests.post(
            f"{self.connection_string}/dedupe_train",
            cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
            data=json.dumps(data),
        )

    def dedupe_get_clusters(self):
        return requests.get(
            f"{self.connection_string}/dedupe_get_clusters",
            cookies={"session_flask": st.session_state[Variables.GB_SESSION_ID]},
        ).json()

    # ZINGG
    def prepare_zingg(self, dedupe_type_dict, dedupe_data) -> json:
        data = {}
        data["dedupe_type_dict"] = dedupe_type_dict
        data["dedupe_data"] = dedupe_data
        return requests.post(
            f"{self.connection_string}/prepare_zingg",
            cookies={
                "session_flask": f"{st.session_state[Variables.GB_SESSION_ID]}-{st.session_state[Variables.SB_LOADED_DATAFRAME_HASH]}"
            },
            data=json.dumps(data),
        )

    def run_zingg_phase(self, phase) -> json:
        data = {}
        data["phase"] = phase
        return requests.post(
            f"{self.connection_string}/run_zingg_phase",
            cookies={
                "session_flask": f"{st.session_state[Variables.GB_SESSION_ID]}-{st.session_state[Variables.SB_LOADED_DATAFRAME_HASH]}"
            },
            data=json.dumps(data),
        )

    def zingg_clear(self) -> json:
        return requests.post(
            f"{self.connection_string}/zingg_clear",
            cookies={
                "session_flask": f"{st.session_state[Variables.GB_SESSION_ID]}-{st.session_state[Variables.SB_LOADED_DATAFRAME_HASH]}"
            },
        )

    def zingg_unmarked_pairs(self) -> json:
        return requests.get(
            f"{self.connection_string}/zingg_unmarked_pairs",
            cookies={
                "session_flask": f"{st.session_state[Variables.GB_SESSION_ID]}-{st.session_state[Variables.SB_LOADED_DATAFRAME_HASH]}"
            },
        ).json()

    def zingg_mark_pairs(self, marked_df) -> json:
        data = {}
        data["marked_df"] = marked_df
        return requests.post(
            f"{self.connection_string}/zingg_mark_pairs",
            cookies={
                "session_flask": f"{st.session_state[Variables.GB_SESSION_ID]}-{st.session_state[Variables.SB_LOADED_DATAFRAME_HASH]}"
            },
            data=json.dumps(data),
        )

    def zingg_get_stats(self) -> json:
        return requests.get(
            f"{self.connection_string}/zingg_get_stats",
            cookies={
                "session_flask": f"{st.session_state[Variables.GB_SESSION_ID]}-{st.session_state[Variables.SB_LOADED_DATAFRAME_HASH]}"
            },
        ).json()

    def zingg_get_clusters(self) -> json:
        return requests.get(
            f"{self.connection_string}/zingg_get_clusters",
            cookies={
                "session_flask": f"{st.session_state[Variables.GB_SESSION_ID]}-{st.session_state[Variables.SB_LOADED_DATAFRAME_HASH]}"
            },
        ).json()

    # DATA CLEANING
    def clean_dataframe_dataprep(self, dataframe_in_json, custom_pipeline) -> json:
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["custom_pipeline"] = custom_pipeline
        return requests.post(
            f"{self.connection_string}/clean_dataframe_dataprep", data=json.dumps(data)
        ).json()

    def fuzzy_match_dataprep(
        self, dataframe_in_json, col, cluster_method, df_name, ngram, radius, block_size
    ) -> json:
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["col"] = col
        data["cluster_method"] = cluster_method
        data["df_name"] = df_name
        data["ngram"] = ngram
        data["radius"] = radius
        data["block_size"] = block_size
        return requests.post(
            f"{self.connection_string}/fuzzy_match_dataprep", data=json.dumps(data)
        ).json()

    def structure_detection(self, series_in_json, exception_chars, compress) -> json:
        data = {}
        data["series_in_json"] = series_in_json
        data["exception_chars"] = exception_chars
        data["compress"] = compress
        return requests.post(
            f"{self.connection_string}/structure_detection", data=json.dumps(data)
        ).json()
    
    def calculate_data_extraction_evaluation_scores(
            self, config_dict, df_chosen_column) -> json:
        data = {}
        data["config_dict"] = config_dict
        data["df_chosen_column"] = df_chosen_column.to_json()
        return requests.post(
            f"{self.connection_string}/calculate_data_extraction_evaluation_scores", data=json.dumps(data)
        ).json()
    
    def perform_data_extraction_clustering(
            self, config_dict="", original_df="", df_to_cluster="") -> json:
        data = {}
        data["config_dict"] = config_dict
        data["original_df"] = original_df.to_json()
        data["df_to_cluster"] = df_to_cluster
        return requests.post(
            f"{self.connection_string}/perform_data_extraction_clustering", data=json.dumps(data)
        ).json()