from typing import Dict

import pandas as pd

from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import ColumnRuleFilter
from src.backend.RuleFinding.VR.ValueRuleElement import ValueRuleElement
from src.backend.RuleFinding.VR.ValueRuleFactory import ValueRuleFactory
from src.backend.RuleFinding.VR.ValueRuleRepo import ValueRuleRepo
from src.backend.RuleFinding.CR.ColumnRuleFactory import ColumnRuleFactory
from src.backend.RuleFinding.CR.ColumnRuleRepo import ColumnRuleRepo
from src.backend.RuleFinding.AR.AssociationRuleFinder import AssociationRuleFinder
from src.shared.enums import FiltererEnum
from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import (
    ColumnRuleFilter_ZScore,
)
from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import (
    ColumnRuleFilter_Entropy,
)
from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import (
    ColumnRuleFilterCMetric,
)
import config as cfg


class RuleMediator:
    def __init__(self, df_ohe, original_df):
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
            max_potential_confidence,
            g3_threshold,
            fi_threshold,
    ) -> None:
        ar_df = self._find_association_rules(
            self.df_ohe, abs_min_support, rule_length, speed, confidence
        )

        cfg.logger.debug(
            "Dataframe with association rules created."
            + " Has %s columns.", ar_df.shape[0]
        )

        # Maak een dict van ValueRules aan in de VR Factory
        vr_dict: Dict[
            str, ValueRuleElement
        ] = self.value_rule_factory.transform_ar_dataframe_to_value_rules_dict(ar_df)

        # Maak een VR Repo aan door de dict van ValueRules mee te geven
        self.value_rule_repo = ValueRuleRepo(vr_dict)

        # Roep get_filtered methode aan op de Repo
        list_of_strings_that_represent_cr = self.value_rule_repo.filter_out_column_rule_strings_from_dict_of_value_rules(
            min_support=1-speed,
            max_potential_confidence=max_potential_confidence,
        )
        # De overige ValueRules worden gebruikt om opnieuw een dict aan te maken in de CR Factory
        cr_dict = self.column_rule_factory.create_dict_of_dict_of_column_rules_from_list_of_strings(
            list_of_strings_that_represent_cr
        )

        # Maak een CR Repo aan door de dict van ColumnRules mee te geven
        self.column_rule_repo = ColumnRuleRepo(cr_dict)
        # Roep getInteresting Rules methode aan op de Repo -> Verschillende implementaties en RETURN deze.
        self.column_rule_repo.keep_only_interesting_column_rules(
            filterer=ColumnRuleFilterCMetric(
                g3_threshold=g3_threshold, fi_threshold=fi_threshold, c_threshold=quality
            ),
            confidence_bound=confidence,
        )

    def get_column_rule_from_string(self, rule_string: str):
        return self.column_rule_factory.expand_single_column_rule(rule_string)

    # Waarschijnlijk alle onderstaande methoden niet nodig
    def get_all_column_rules(self):
        return {
            **self.get_cr_definitions_dict(),
            **self.get_cr_with_100_confidence_dict(),
            **self.get_cr_without_100_confidence_dict(),
        }

    def get_cr_definitions_dict(self):
        return self.column_rule_repo.get_definitions_dict()

    def get_cr_with_100_confidence_dict(self):
        return self.column_rule_repo.get_cr_with_100_confidence_dict()

    def get_cr_without_100_confidence_dict(self):
        return self.column_rule_repo.get_cr_without_100_confidence_dict()

    def get_non_definition_column_rules_dict(self):
        return self.column_rule_repo.get_non_definitions_dict()

    def _find_association_rules(
        self,
        df_ohe: pd.DataFrame,
        abs_min_support, rule_length, speed, confidence
    ):
        self.association_rule_finder = AssociationRuleFinder(
            df_ohe,
            rule_length,
            abs_min_support,
        )
        return self.association_rule_finder.get_association_rules()

