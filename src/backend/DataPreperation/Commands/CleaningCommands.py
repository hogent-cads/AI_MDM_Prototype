from abc import ABC, abstractmethod
import re

import pandas as pd


class CleaningCommand(ABC):

    @abstractmethod
    def execute(self, series: pd.Series) -> pd.Series:
        raise Exception("Not implemented Exception")


class CleaningCommand_Trim(CleaningCommand):

    def __init__(self, series: pd.Series) -> None:
        self.series = series

    def execute(self) -> pd.Series:
        return self.series.apply(lambda x: str.strip(str(x)))


class CleaningCommand_StringToFloat(CleaningCommand):
    """ Gets the "last" floating point number from a string. 
    """

    def __init__(self, series: pd.Series) -> None:
        self.series = series

    def execute(self) -> pd.Series:
        return self.series.apply(
            lambda stringValue: self._extract_float_from_string(stringValue))

    def _extract_float_from_string(self, s: str) -> float:
        lst = re.findall(r"[-+]?\d*\.\d+|\d+", str(s))
        if len(lst) > 0:
            return max([float(i) for i in lst])
        else:
            return pd.NA
