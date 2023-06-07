from typing import Sequence

from src.backend.RuleFinding.CR.ColumnRule import ColumnRule
from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import ColumnRuleFilter


class ColumnRuleRepo:

    def __init__(self, column_rules: Sequence[ColumnRule]) -> None:
        self.column_rules = column_rules

    def keep_only_interesting_column_rules(
            self,
            filterer: ColumnRuleFilter,
            confidence_bound: float) -> None:
        # Only keep those column rules that achieve the required minimum confidence
        self.column_rules = [rule for rule in self.column_rules
                             if rule.confidence >= confidence_bound]
        self.column_rules = filterer.execute(rules=self.column_rules)

    def get_column_rules(self):
        return self.column_rules
