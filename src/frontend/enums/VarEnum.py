# importing enum for enumerations
import enum


# creating enumerations using class
class VarEnum(str, enum.Enum):
    # Configuration
    CFG_WEBSOCKET_SERVER_URL = "WEBSOCKET_SERVER_URL"

    # States
    ST_DD_LABELING = "LabelRecords_get_all_unmarked_pairs"
    ST_DD_REDIRECT_CLUSTERING = "Zingg_ViewClusters_get_clusters"
    ST_DD_CLUSTERING = "Zingg_ViewClusters"

    ST_RL_RULES = "BekijkRules"
    ST_RL_SUGGESTIONS = "BekijkSuggesties"

    # Global
    GB_CURRENT_STATE = "currentState"
    GB_SESSION_MAP = "session_map"
    GB_SESSION_ID = "session_flask_local_id"
    GB_CURRENT_SEQUENCE_NUMBER = "current_seq"

    # Sidebar
    SB_LOADED_DATAFRAME = "dataframe"
    SB_LOADED_DATAFRAME_NAME = "dataframe_name"
    SB_LOADED_DATAFRAME_SEPARATOR = "dataframe_separator"
    SB_LOADED_DATAFRAME_HASH = "dataframe_hash"
    SB_LOADED_DATAFRAME_ID = "dataframe_id"
    SB_TYPE_HANDLER = "type_handler"
    SB_CURRENT_FUNCTIONALITY = "current_functionality"
    SB_CURRENT_PROFILING = "current_profiling"

    # Data Display Component
    DDC_FORCE_RELOAD_CACHE = "force_reload_cache"

    # Data Cleaning
    DC_PIPELINE = "pipeline"
    DC_CLEANED_COLUMN = "cleaned_column_from_pipeline"

    # Data Profiling
    DP_PANDAS_PROFILE = "generated_pandas_profile"
    DP_DATAPREP_PROFILE = "generated_dataprep_profile"

    # Data Extraction

    # Deduplication
    DD_TYPE_DICT = "dedupe_type_dict"
    DD_CURRENT_LABEL_ROUND = "zingg_current_label_round"
    DD_LABEL_STATS = "zingg_stats"

    DD_CLUSTER_DF = "zingg_cluster_df"

    # Rule-Learning
