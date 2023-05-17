# importing enum for enumerations
import enum

# creating enumerations using class
class VarEnum(str, enum.Enum):

    # Configuration
    cfg_WEBSOCKET_SERVER_URL = "WEBSOCKET_SERVER_URL"

    # States
    st_DD_Labeling = "LabelRecords_get_all_unmarked_pairs"
    st_DD_REDIRECT_Clustering = "Zingg_ViewClusters_get_clusters"
    st_DD_Clustering = "Zingg_ViewClusters"

    st_RL_Rules = "BekijkRules"
    st_RL_Suggestions = "BekijkSuggesties"

    # Global
    gb_CURRENT_STATE = "currentState"
    gb_SESSION_MAP = "session_map"
    gb_SESSION_ID = "session_flask_local_id"
    gb_CURRENT_SEQUENCE_NUMBER = "current_seq"

    # Sidebar
    sb_LOADED_DATAFRAME = "dataframe"
    sb_LOADED_DATAFRAME_NAME = "dataframe_name"
    sb_LOADED_DATAFRAME_separator = "dataframe_separator"
    sb_LOADED_DATAFRAME_HASH = "dataframe_hash"
    sb_LOADED_DATAFRAME_ID = "dataframe_id"
    sb_TYPE_HANDLER = "type_handler"
    sb_CURRENT_FUNCTIONALITY = "current_functionality"
    sb_CURRENT_PROFILING = "current_profiling"

    # Data Display Component
    ddc_FORCE_RELOAD_CACHE = "force_reload_cache"

    # Data Cleaning
    dc_PIPELINE = "pipeline"
    dc_CLEANED_COLUMN = "cleaned_column_from_pipeline"



    # Data Profiling
    dp_PANDAS_PROFILE = "generated_pandas_profile"
    dp_DATAPREP_PROFILE = "generated_dataprep_profile"


    # Data Extraction



    # Deduplication
    dd_TYPE_DICT = "dedupe_type_dict"
    dd_CURRENT_LABEL_ROUND = "zingg_current_label_round"
    dd_LABEL_STATS = "zingg_stats"

    dd_CLUSTER_DF = "zingg_cluster_df"



    # Rule-Learning