import json
from typing import List

import pandas as pd


class ColumnRuleView:
    def __init__(
        self, rule_string: str, value_mapping, confidence, idx_to_correct: List[int]
    ):
        self.value_mapping = value_mapping
        self.rule_string = rule_string
        self.idx_to_correct = idx_to_correct
        self.confidence = confidence

    def to_json(self):
        # Return a json representation of this object
        return json.dumps(
            {
                "rule_string": self.rule_string,
                "value_mapping": self.value_mapping.to_json(),
                "idx_to_correct": json.dumps(self.idx_to_correct),
                "confidence": self.confidence,
            }
        )

    @staticmethod
    def parse_from_json(json_string):
        data = json.loads(json_string)
        return ColumnRuleView(
            rule_string=data["rule_string"],
            value_mapping=pd.DataFrame(json.loads(data["value_mapping"])),
            idx_to_correct=json.loads(data["idx_to_correct"]),
            confidence=data["confidence"],
        )
