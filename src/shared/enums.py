import enum


class BinningEnum(str, enum.Enum):
    EQUAL_BINS= "equal_bins"
    K_MEANS= "k_means"


class CleaningEnum(str, enum.Enum):
    STRING_TO_FLOAT= "string_to_float"
    TRIM= "trim"


class DroppingEnum(str, enum.Enum):
    DROP_WITH_UNIQUENESS_BOUND= "drop_with_uniqueness_bound"
    DROP_WITH_LOWER_BOUND= "drop_with_lower_bound"
    DROP_WITH_UPPER_BOUND= "drop_with_upper_bound"

    DROP_NAN = "drop_nan"


class FiltererEnum(str, enum.Enum):
    Z_SCORE = "z_score"
    ENTROPY = "entropy"
    C_METRIC = "c_metric"
