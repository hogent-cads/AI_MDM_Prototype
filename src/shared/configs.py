import json
from typing import Dict

from src.shared.enums import BinningEnum


class CleaningConfig:
    def __init__(self, cleaning_options):
        self.cleaning_options = cleaning_options

    def to_json(self):
        return json.dumps(self.__dict__)


class RuleFindingConfig:

    def __init__(self,
                 cols_to_use,
                 rule_length: int,
                 confidence: float,
                 speed,
                 quality: int,
                 abs_min_support: int,
                 g3_threshold: float,
                 fi_threshold: float) -> None:
        self.rule_length = rule_length
        self.confidence = confidence
        self.speed = speed
        self.quality = quality
        self.abs_min_support = abs_min_support
        self.cols_to_use = cols_to_use
        self.g3_threshold = g3_threshold
        self.fi_threshold = fi_threshold

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def create_from_json(json_string):
        data = json.loads(json_string)
        return RuleFindingConfig(
            rule_length=data["rule_length"],
            confidence=data["confidence"],
            speed=data["speed"],
            quality=data["quality"],
            abs_min_support=data["abs_min_support"],
            cols_to_use=data["cols_to_use"],
            g3_threshold=data["g3_threshold"],
            fi_threshold=data["fi_threshold"]
        )

