import json
from typing import List

from src.frontend.Handler.IHandler import IHandler
from src.backend.DomainController import DomainController
from src.shared.Views.ColumnRuleView import ColumnRuleView


class LocalHandler(IHandler):
    def __init__(self) -> None:
        self.dc = DomainController()

    def get_column_rules(
        self, dataframe_in_json, rule_finding_config_in_json, seq
    ) -> List[ColumnRuleView]:
        return {
            k: ColumnRuleView.parse_from_json(v)
            for (k, v) in json.loads(
                self.dc.get_all_column_rules_from_df_and_config(
                    dataframe_in_json, rule_finding_config_in_json, seq
                )
            ).items()
        }

    def get_column_rule_from_string(self, dataframe_in_json, rule_string):
        return ColumnRuleView.parse_from_json(
            self.dc.get_column_rule_from_string(
                dataframe_in_json=dataframe_in_json, rule_string=rule_string
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
