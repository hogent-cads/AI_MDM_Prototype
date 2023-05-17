# importing enum for enumerations
import enum

# creating enumerations using class
class DialogEnum(str, enum.Enum):

    # GLOBAL
    gb_PAGE_TITLE = "AI MDM Tool"

    # Sidebar
    sb_PREVIOUS_STATE_button = "Go back to previous phase"

    sb_FUNCTIONALITY_selectbox = "Functionality"
    sb_FUNCTIONALITY_option_DATA_CLEANING = "Data Cleaning"
    sb_FUNCTIONALITY_option_DATA_PROFILING = "Data Profiling"
    sb_FUNCTIONALITY_option_DATA_EXTRACTION = "Data Extraction"
    sb_FUNCTIONALITY_option_DEDUPLICATION = "Data Deduplication"
    sb_FUNCTIONALITY_option_RULE_LEARNING = "Rule Learning"

    sb_DATA_PROFILING_option_pandas = "Pandas Profiling"
    sb_DATA_PROFILING_option_dataprep = "Dataprep Profiling"

    sb_TYPE_HANDLER_radio = "Type Handler: "
    sb_TYPE_HANDLER_option_REMOTE = "Remote"
    sb_TYPE_HANDLER_option_LOCAL = "Local"

    sb_PREVIOUS_RESULTS = "Previous results on the dataset"

    sb_UPLOAD_DATASET = "Choose a .csv file"
    sb_separator = "separator"
    sb_OPTIONAL_separator = "Optional separator"
    sb_OPTIONAL_separator_DESCRIPTION = "Change when the separator is not a ','"

    sb_DOWNLOAD_DATASET = "Download currently loaded dataset"

    sb_RELOAD_BUTTON = "Reload"

    # Data Cleaning
    dc_CLEANING_PIPELINES = "Cleaning Pipelines"
    dc_CLEANING_PIPELINES_CURRENT = "Current Cleaning Pipeline"
    dc_CLEANING_method_LOWERCASE = "Transform data to lowercase"
    dc_CLEANING_method_LOWERCASE_description = "Convert all characters to lowercase."

    dc_CLEANING_method_UPPERCASE = "Transform data to uppercase"
    dc_CLEANING_method_UPPERCASE_description = "Convert all characters to uppercase."

    dc_CLEANING_method_FILLNA = "Fill empty data cells"
    dc_CLEANING_method_FILLNA_description = "By default, replaces all null values with NaN. Otherwise specify a specific value to replace null values. You can use MEAN or MEDIAN or MODE as value"

    dc_CLEANING_method_REMOVE_DIGITS = "Remove digits from data"
    dc_CLEANING_method_REMOVE_DIGITS_description = "Removes all digits from data"

    dc_CLEANING_method_REMOVE_PUNCTUATION = "Remove punctuation from data"
    dc_CLEANING_method_REMOVE_PUNCTUATION_description = "Remove all punctuation marks defined in Python’s string.punctuation."

    dc_CLEANING_method_REMOVE_ACCENTS = "Remove accents from data"
    dc_CLEANING_method_REMOVE_ACCENTS_description = "Remove accents (diacritic marks) from the text."

    dc_CLEANING_method_REMOVE_STOPWORDS = "Remove stopwords from data"
    dc_CLEANING_method_REMOVE_STOPWORDS_description = "Remove common words. By default, the set of stopwords to remove is NLTK’s English stopwords. Or provide a custom set of stopwords, separated by a comma."

    dc_CLEANING_method_REMOVE_WHITESPACE = "Remove whitespace from data"
    dc_CLEANING_method_REMOVE_WHITESPACE_description = "Remove extra spaces (two or more) along with tabs and newlines. Leading and trailing spaces are also removed."

    dc_CLEANING_method_REMOVE_BRACKETED = "Remove brackeded text from data"
    dc_CLEANING_method_REMOVE_BRACKETED_description = "Remove text between brackets. The style of the brackets can be specified: round, square, curly or angle."

    dc_CLEANING_method_REMOVE_PREFIXED = "Remove prefixed from data"
    dc_CLEANING_method_REMOVE_PREFIXED_description = "Remove substrings that start with the prefix(es) specified in the prefix parameter."

    dc_CLEANING_method_REMOVE_HTML = "Remove HTML-tags from data"
    dc_CLEANING_method_REMOVE_HTML_description = "Removes all HTML-tags from data"

    dc_CLEANING_method_REMOVE_URL = "Remove URL from data"
    dc_CLEANING_method_REMOVE_URL_description = "Replace URLs with the value. Substrings that start with “http” or “www” are considered URLs."

    dc_CLEANING_method_selection = "Select the cleaning method"

    dc_CLEANING_ADD_PIPELINE = "Add to pipeline"
    dc_CLEANING_CLEAR_PIPELINE = "Clear pipeline"
    dc_CLEANING_APPLY_PIPELINE_COLUMN = "Apply pipeline to column"
    dc_CLEANING_APPLY_PIPELINE_ALL = "Apply pipeline to all columns"
    dc_CLEANING_SELECT_COLUMN = "Select the column that you want to clean:"

    dc_CLEANING_CHANGES_APPLIED = "All columns cleaned, changes were applied to the data"
    dc_CLEANING_COLUMN_CLEANED = "Cleaned Column: "
    dc_CLEANING_SAVE_COLUMN = "Save column"
    dc_CLEANING_COLUMN_SAVED = "Column saved"

    dc_CLEANING_CURRENT_PIPELINE = "Current pipeline: "
    dc_CLEANING_SELECT_BRACKET = "Select the bracket type"

    dc_CLEANING_FILLNA_value_MEAN = "MEAN"
    dc_CLEANING_FILLNA_value_MEDIAN = "MEDIAN"
    dc_CLEANING_FILLNA_value_MODE = "MODE"


    # Data Profiling



    # Data Extraction



    # Deduplication

    dd_DEDUPLICATION = "Deduplication"
    dd_DEDUPLICATION_COLUMN_SELECTION = "Select which columns you want to use during the deduplication proces:"
    dd_DEDUPLICATION_COLUMN_SELECTION_OVERVIEW = "Settings that will be used during active learning:"
    dd_DEDUPLICATION_CHANGE_TYPE_btn = "Change type"
    dd_DEDUPLICATION_START_btn = "Start training"

    dd_DEDUPLICATION_LABEL_selectbox = "Choice:"
    dd_DEDUPLICATION_LABEL_is_a_match = "is a match"
    dd_DEDUPLICATION_LABEL_is_not_a_match = "is a not match"
    dd_DEDUPLICATION_LABEL_unsure = "unsure"

    dd_DEDUPLICATION_PAIRS_TO_MARK = "Pairs to mark:"
    dd_DEDUPLICATION_UPDATE_btn = "Update and give new pairs"
    dd_DEDUPLICATION_CLEAR_btn = "Clear all previous labels (Rerun)"
    dd_DEDUPLICATION_FINISH_btn = "Finish labeling, go to clustering"

    dd_DEDUPLICATION_MODEL_FAIL_MESSAGE = "The model could not be created. Please label more data and try again."

    dd_DEDUPLICATION_PREDICTION = "Prediction:"
    dd_DEDUPLICATION_PREDICTION_SCORE = "Prediction score:"

    # Rule-Learning

