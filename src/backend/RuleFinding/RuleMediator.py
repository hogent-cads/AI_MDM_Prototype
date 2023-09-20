from typing import Dict, Sequence, Set

import pandas as pd
import hashlib

from src.backend.RuleFinding.VR.ValueRule import ValueRule
from src.backend.RuleFinding.VR.ValueRuleFactory import ValueRuleFactory
from src.backend.RuleFinding.VR.ValueRuleRepo import ValueRuleRepo
from src.backend.RuleFinding.CR.ColumnRuleFactory import ColumnRuleFactory
from src.backend.RuleFinding.CR.ColumnRuleRepo import ColumnRuleRepo
from src.backend.RuleFinding.CR.ColumnRule import ColumnRule
from src.backend.RuleFinding.AR.AssociationRuleFinder import AssociationRuleFinder
from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import (
    ColumnRuleFilterCMetric,
)
from src.backend.RuleFinding.Pyro import Pyro
import config as cfg


class RuleMediator:
    def __init__(self, df_ohe: pd.DataFrame, original_df: pd.DataFrame):
        self.df_ohe = df_ohe
        self.original_df = original_df

        self.association_rule_finder = None
        self.value_rule_repo = None
        self.column_rule_repo = None

        self.value_rule_factory = ValueRuleFactory()
        self.column_rule_factory = ColumnRuleFactory(
            df_dummy=df_ohe, original_df=original_df
        )

    def create_column_rules_from_clean_dataframe(
        self,
        rule_length,
        confidence,
        speed,
        quality,
        abs_min_support,
        g3_threshold,
        fi_threshold,
        pyro,
    ) -> None:
        """
        Create column rules and store them in `self.column_rule_repo`.
        """

        if pyro:
            modelID = hashlib.md5(self.original_df.to_string().encode()).hexdigest()
            rule_strings = Pyro.run_pyro(df2=self.original_df, modelID=modelID)

        else:
            ar_df = self._find_association_rules(
                df_ohe=self.df_ohe,
                abs_min_support=abs_min_support,
                rule_length=rule_length
            )

            cfg.logger.debug(
                "Dataframe with association rules created."
                + " has %s rows.", ar_df.shape[0]
            )

            # Maak een dict van ValueRules aan in de VR Factory
            vr_dict: Dict[
                str, Set[ValueRule]
            ] = self.value_rule_factory.transform_ar_dataframe_to_value_rules_dict(ar_df)

            # Maak een VR Repo aan door de dict van ValueRules mee te geven
            self.value_rule_repo = ValueRuleRepo(vr_dict)

            # Bereken de rule strings die we verder nog gaan bekijken
            # gebaseerd op de support van de waarderegel en de mogelijke confidence
            # die deze regel nog kan bereiken
            rule_strings: Sequence[str] = self.value_rule_repo.filter_column_rule_strings(
                min_support=speed,
                confidence=confidence,
            )
        # De overige ValueRules worden gebruikt om opnieuw een dict aan te maken in de CR Factory
        column_rules: Sequence[ColumnRule] = \
            self.column_rule_factory.create_column_rules_from_strings(
            rule_strings
        )

        # Maak een CR Repo aan door de dict van ColumnRules mee te geven
        self.column_rule_repo = ColumnRuleRepo(column_rules)

        # For now, we only use the c-metric to filter rules.
        self.column_rule_repo.keep_only_interesting_column_rules(
            filterer=ColumnRuleFilterCMetric(
                g3_threshold=g3_threshold,
                fi_threshold=fi_threshold,
                c_threshold=quality
            ),
            confidence_bound=confidence,
        )

    def get_column_rule_from_string(self, rule_string: str):
        return self.column_rule_factory.expand_single_column_rule(rule_string)

    def get_all_column_rules(self):
        return self.column_rule_repo.get_column_rules()

    def _find_association_rules(
        self,
        df_ohe: pd.DataFrame,
        abs_min_support: int,
        rule_length: int
    ):
        self.association_rule_finder = AssociationRuleFinder(
            df_ohe,
            rule_length,
            abs_min_support,
        )
        return self.association_rule_finder.get_association_rules()

    @staticmethod
    def _preprocess_association_rules(ar_df):  # TODO: remove this method
        """
        Filter some rows from the ar_df dataframe.
        Namely, rows that have the same antecedent and that deal with the same consequent
        column.
        Only keep one of these rows, namely the one with the highest confidence.
        """
        ar_df["consequent_column_name"] = ar_df["consequents"].apply(
            lambda con_set: list(con_set)[0].split("_")[0]  # This assumes no _ in column names
        )
        grouped = ar_df.groupby(["antecedents", "consequent_column_name"]).max()

        # Add 'consequents' column to the index of grouped
        grouped.set_index("consequents", append=True, inplace=True)

        print("grouped association rules")
        print(grouped)

        return ar_df.set_index(
            ["antecedents", "consequent_column_name", "consequents"]).loc[grouped.index,
              :].reset_index().drop("consequent_column_name", axis="columns")
