from typing import Dict, Set, List

import numpy as np

from src.backend.RuleFinding.VR.ValueRule import ValueRule
import config as cfg


class ValueRuleRepo:
    def __init__(self, value_rules_dict: Dict[str, Set[ValueRule]]):
        self.value_rules_dict: Dict[str, Set[ValueRule]] = value_rules_dict

    def filter_column_rule_strings(
        self, min_support: float, confidence: float
    ) -> List[str]:
        """
        TODO!!
        """
        self.value_rules_dict: Dict[
            str, Set[ValueRule]
        ] = self._filter_low_support_rules(min_support)

        potential_conf_dict = self._create_potential_conf_dict_from_value_rules()
        cfg.logger.debug("potential_conf_dict %s", potential_conf_dict)
        cfg.logger.debug("potential_conf_dict has %s keys", len(potential_conf_dict))

        # Filter out rules that have a low maximum confidence.
        filtered = {
            rs: max_conf
            for rs, max_conf in potential_conf_dict.items()
            if max_conf >= confidence
        }

        cfg.logger.debug("potential_conf_dict has %s keys", len(potential_conf_dict))
        cfg.logger.debug("filtered dictionary has %s keys", len(filtered))

        return filtered.keys()

    def _create_potential_conf_dict_from_value_rules(self):
        potential_conf_dict: Dict[str, float] = {
            rs: self._calculate_max_confidence(vrs)
            for rs, vrs in self.value_rules_dict.items()
        }
        return potential_conf_dict

    def _filter_low_support_rules(self, min_support) -> Dict[str, Set[ValueRule]]:
        """Remove all entries from the dictionary `self.value_rules_dict` whose total
        support is currently not greater or equal than `min_support`.

        self.value_rules_dict: dictionary mapping rule strings,
                               i.e. strings of the form (A,B => C)
                               to a set of value rules involving those columns.
        min_support: a float (0.0 <= min_support <= 1.0)

        returns: a dictionary of kept entries
        """
        cfg.logger.info(
            "Trying to remove rule_strings"
            + " for which total support is less than %s",  min_support
        )

        removed_rs: Dict[str, Set[ValueRule]] = {}
        kept_rs: Dict[str, Set[ValueRule]] = {}
        for rs, value_rules in self.value_rules_dict.items():
            support = np.sum([vr.support for vr in value_rules])

            cfg.logger.debug("value rules with %s together have support %s",
                             rs, support)
            cfg.logger.debug("The value rules are %s",
                             " ".join(str(value_rule) for value_rule in value_rules))

            if support < min_support:  # remove this one
                removed_rs[rs] = self.value_rules_dict[rs]
            else:
                kept_rs[rs] = self.value_rules_dict[rs]

        cfg.logger.info(
            "Removed %s rule strings because of low support"
            + " kept %s. Minimum support has value %s",
            len(removed_rs),
            len(kept_rs),
            min_support
        )

        return kept_rs

    def _calculate_max_confidence(self, value_rules: Set[ValueRule]) -> float:
        """
        Calculate the maximum confidence that a column rule might obtain based
        on the confidences and supports of the current value rules for that potential
        column rule.
        Do this by assuming that all values that are currently not mapped are correct.

        value_rules: a set of value rules. These should all pertain to the same columns

        returns: a float that represents the maximum confidence level that
        this rule can ever achieve
        """
        cfg.logger.debug(
            "Calculating max confidence for %s", ';'.join(str(_) for _ in value_rules)
        )
        support = np.sum([vr.support for vr in value_rules])
        cfg.logger.debug("The value rules together have support %s", support)

        weighted_confidence = np.sum([vr.support * vr.confidence for vr in value_rules])

        cfg.logger.debug("Weighted confidence: %s", weighted_confidence)

        return weighted_confidence + (1 - support) * 1.0
