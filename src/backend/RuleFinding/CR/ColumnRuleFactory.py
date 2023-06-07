from typing import Sequence, List

import pandas as pd

import config as cfg
from src.backend.RuleFinding.CR.ColumnRule import ColumnRule


class ColumnRuleFactory:
    def __init__(self, df_dummy: pd.DataFrame, original_df: pd.DataFrame) -> None:
        self.df_dummy = df_dummy
        self.original_df = original_df

    def create_column_rules_from_strings(
        self, cr_rule_strings
    ) -> Sequence[ColumnRule]:
        rule_list: List[ColumnRule] = []

        # For progress bar
        index_mod = len(cr_rule_strings) // 10 + 1

        for index, rule in enumerate(cr_rule_strings):
            # Log progress
            if index % index_mod == 0:
                cfg.logger.info("%s / %s",  index, len(cr_rule_strings))

            rule_list.append(self.expand_single_column_rule(rule))

        return rule_list

    def expand_single_column_rule(self, rule_string: str) -> ColumnRule:
        return ColumnRule(
            rule_string=rule_string, original_df=self.original_df, value_mapping=True
        )
