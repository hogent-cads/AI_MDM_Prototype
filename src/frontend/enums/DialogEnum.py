# importing enum for enumerations
import enum


# creating enumerations using class
class DialogEnum(str, enum.Enum):
    # GLOBAL
    GB_PAGE_TITLE = "AI MDM Tool"

    # Sidebar
    SB_PREVIOUS_STATE_BUTTON = "Go back to previous phase"

    SB_FUNCTIONALITY_SELECTBOX = "Functionality"
    SB_FUNCTIONALITY_OPTION_DATA_CLEANING = "Data Cleaning"
    SB_FUNCTIONALITY_OPTION_DATA_PROFILING = "Data Profiling"
    SB_FUNCTIONALITY_OPTION_DATA_EXTRACTION = "Data Extraction"
    SB_FUNCTIONALITY_OPTION_DEDUPLICATION = "Data Deduplication"
    SB_FUNCTIONALITY_OPTION_RULE_LEARNING = "Rule Learning"

    SB_DATA_PROFILING_OPTION_PANDAS = "Pandas Profiling"
    SB_DATA_PROFILING_OPTION_DATAPREP = "Dataprep Profiling"

    SB_TYPE_HANDLER_RADIO = "Type Handler: "
    SB_TYPE_HANDLER_OPTION_REMOTE = "Remote"
    SB_TYPE_HANDLER_OPTION_LOCAL = "Local"

    SB_PREVIOUS_RESULTS = "Previous results on the dataset"

    SB_UPLOAD_DATASET = "Choose a .csv file"
    SB_SEPARATOR = "separator"
    SB_OPTIONAL_SEPARATOR = "Optional separator"
    SB_OPTIONAL_SEPARATOR_DESCRIPTION = "Change when the separator is not a ','"

    SB_DOWNLOAD_DATASET = "Download currently loaded dataset"

    SB_RELOAD_BUTTON = "Reload"

    # Data Cleaning
    DC_CLEANING_PIPELINES = "Cleaning Pipelines"
    DC_CLEANING_PIPELINES_CURRENT = "Current Cleaning Pipeline"
    DC_CLEANING_METHOD_LOWERCASE = "Transform data to lowercase"
    DC_CLEANING_METHOD_LOWERCASE_DESCRIPTION = "Convert all characters to lowercase."

    DC_CLEANING_METHOD_UPPERCASE = "Transform data to uppercase"
    DC_CLEANING_METHOD_UPPERCASE_DESCRIPTION = "Convert all characters to uppercase."

    DC_CLEANING_METHOD_FILLNA = "Fill empty data cells"
    DC_CLEANING_METHOD_FILLNA_DESCRIPTION = "By default, replaces all null values with NaN. " \
                                            "Otherwise specify a " \
                                            "specific value to replace null values. You can " \
                                            "use MEAN or MEDIAN or " \
                                            "MODE as value"

    DC_CLEANING_METHOD_REMOVE_DIGITS = "Remove digits from data"
    DC_CLEANING_METHOD_REMOVE_DIGITS_DESCRIPTION = "Removes all digits from data"

    DC_CLEANING_METHOD_REMOVE_PUNCTUATION = "Remove punctuation from data"
    DC_CLEANING_METHOD_REMOVE_PUNCTUATION_DESCRIPTION = "Remove all punctuation marks " \
                                                        "defined in Python’s " \
                                                        "string.punctuation."

    DC_CLEANING_METHOD_REMOVE_ACCENTS = "Remove accents from data"
    DC_CLEANING_METHOD_REMOVE_ACCENTS_DESCRIPTION = "Remove accents (diacritic marks) from " \
                                                    "the text."

    DC_CLEANING_METHOD_REMOVE_STOPWORDS = "Remove stopwords from data"
    DC_CLEANING_METHOD_REMOVE_STOPWORDS_DESCRIPTION = "Remove common words. By default, the " \
                                                      "set of stopwords to " \
                                                      "remove is NLTK’s English stopwords. " \
                                                      "Or provide a custom set of" \
                                                      " stopwords, separated by a comma."

    DC_CLEANING_METHOD_REMOVE_WHITESPACE = "Remove whitespace from data"
    DC_CLEANING_METHOD_REMOVE_WHITESPACE_DESCRIPTION = "Remove extra spaces (two or more) " \
                                                       "along with tabs and " \
                                                       "newlines. Leading and trailing " \
                                                       "spaces are also removed."

    DC_CLEANING_METHOD_REMOVE_BRACKETED = "Remove bracketed text from data"
    DC_CLEANING_METHOD_REMOVE_BRACKETED_DESCRIPTION = "Remove text between brackets. The " \
                                                      "style of the brackets can be " \
                                                      "specified: round, square, curly or " \
                                                      "angle."

    DC_CLEANING_METHOD_REMOVE_PREFIXED = "Remove prefixed from data"
    DC_CLEANING_METHOD_REMOVE_PREFIXED_DESCRIPTION = "Remove substrings that start with the " \
                                                     "prefix(es) specified in " \
                                                     "the prefix parameter."

    DC_CLEANING_METHOD_REMOVE_HTML = "Remove HTML-tags from data"
    DC_CLEANING_METHOD_REMOVE_HTML_DESCRIPTION = "Removes all HTML-tags from data"

    DC_CLEANING_METHOD_REMOVE_URL = "Remove URL from data"
    DC_CLEANING_METHOD_REMOVE_URL_DESCRIPTION = "Replace URLs with the value. Substrings " \
                                                "that start with “http” or " \
                                                "“www” are considered URLs."

    DC_CLEANING_METHOD_SELECTION = "Select the cleaning method"

    DC_CLEANING_ADD_PIPELINE = "Add to pipeline"
    DC_CLEANING_CLEAR_PIPELINE = "Clear pipeline"
    DC_CLEANING_APPLY_PIPELINE_COLUMN = "Apply pipeline to column"
    DC_CLEANING_APPLY_PIPELINE_ALL = "Apply pipeline to all columns"
    DC_CLEANING_SELECT_COLUMN = "Select the column that you want to clean:"

    DC_CLEANING_CHANGES_APPLIED = "All columns cleaned, changes were applied to the data"
    DC_CLEANING_COLUMN_CLEANED = "Cleaned Column: "
    DC_CLEANING_SAVE_COLUMN = "Save column"
    DC_CLEANING_COLUMN_SAVED = "Column saved"

    DC_CLEANING_CURRENT_PIPELINE = "Current pipeline: "
    DC_CLEANING_SELECT_BRACKET = "Select the bracket type"

    DC_CLEANING_FILLNA_VALUE_MEAN = "MEAN"
    DC_CLEANING_FILLNA_VALUE_MEDIAN = "MEDIAN"
    DC_CLEANING_FILLNA_VALUE_MODE = "MODE"

    # Data Profiling

    # Data Extraction

    # Deduplication

    DD_DEDUPLICATION = "Deduplication"
    DD_DEDUPLICATION_COLUMN_SELECTION = "Select which columns you want to use during the " \
                                        "deduplication proces:"
    DD_DEDUPLICATION_COLUMN_SELECTION_OVERVIEW = "Settings that will be used during active " \
                                                 "learning:"
    DD_DEDUPLICATION_CHANGE_TYPE_BTN = "Change type"
    DD_DEDUPLICATION_START_BTN = "Start training"

    DD_DEDUPLICATION_LABEL_SELECTBOX = "Choice:"
    DD_DEDUPLICATION_LABEL_IS_A_MATCH = "is a match"
    DD_DEDUPLICATION_LABEL_IS_NOT_A_MATCH = "is a not match"
    DD_DEDUPLICATION_LABEL_UNSURE = "unsure"

    DD_DEDUPLICATION_PAIRS_TO_MARK = "Pairs to mark:"
    DD_DEDUPLICATION_UPDATE_BTN = "Update and give new pairs"
    DD_DEDUPLICATION_CLEAR_BTN = "Clear all previous labels (Rerun)"
    DD_DEDUPLICATION_FINISH_BTN = "Finish labeling, go to clustering"

    DD_DEDUPLICATION_MODEL_FAIL_MESSAGE = "The model could not be created. Please label more " \
                                          "data and try again."

    DD_DEDUPLICATION_PREDICTION = "Prediction:"
    DD_DEDUPLICATION_PREDICTION_SCORE = "Prediction score:"

    # Rule-Learning
