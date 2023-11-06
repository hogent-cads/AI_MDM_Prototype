import hashlib
import glob
import os

import pandas as pd
from flask import json, request
from flask_classful import FlaskView, route

from src.backend.RuleFinding.RuleMediator import RuleMediator
from src.backend.Suggestions.SuggestionFinder import SuggestionFinder
from src.backend.DataPreperation.DataPrepper import DataPrepper
from src.backend.DataCleaning.DataFrameCleaner import DataFrameCleaner
from src.shared.configs import RuleFindingConfig
from src.backend.DataCleaning.FuzzyMatcher import FuzzyMatcher
from src.backend.DataCleaning.StructureDetector import StructureDetector
from src.backend.Deduplication.Zingg import Zingg
from src.backend.DataExtraction.DataExtractor import DataExtractor
import config as cfg
from src.shared.views import ColumnRuleView

class DomainController(FlaskView):
    def __init__(self, session_dict={}, app=None) -> None:
        self.session_dict = session_dict
        self.app = app
        self.data_prepper = DataPrepper()
        self.rule_mediator = None
        self.suggestion_finder = None
        self.data_extractor = DataExtractor()

    #  -------------------------------------------------------------------------- 
    #                                 UTILS: PUBLIC API METHODS                               
    #  -------------------------------------------------------------------------- 
    @route("/fetch_file_from_filepath", methods=["POST"])
    def fetch_file_from_filepath(self, filepath: str = ""):
        """
        Fetches a json file from a filepath on the server where the flask app is running.
        This method is used to fetch the results of a previous run of a method. (For example: the results of the rule learning)
        :param filepath: The filepath to fetch the file from
        :type str:
        :return: json file
        """
        if filepath == "":
            data_to_use = json.loads(request.data)
            filepath = data_to_use["filepath"]
        with open(filepath, "r") as json_file:
            content = json_file.read()
        return content


    @route("/get_session_map", methods=["GET", "POST"])
    def get_session_map(self, dataframe_in_json=""):
        """
        Returns the session map of the current session. This is a dictionary that contains the results of previous runs of methods.
        These session maps are stored in the ./storage folder.
        When there isn't a session map stored in the ./storage folder for a specific unique storage id, a new session map is created.
        :param dataframe_in_json: A pandas Dataframe in json format, example of format: df.to_json()
        :type: str
        :return: The session map. An example of what a session map looks like:
        {
        "1":
            {"rules": "storage/[UNIQUE_STORAGE_ID]/[HASH_OF_THE_DATA]/Rule-learning_rules__[HASH_OF_THE_PARAMETERS].json",
            "suggestions": "storage/[HASH_OF_THE_USER]// Rule-learning_suggestions__[HASH_OF_THE_PARAMETERS].json"}
        }

        With:
        [UNIQUE_STORAGE_ID] = When using the API, a unique id is generated for the session. This is stored in a cookie.
        [HASH_OF_THE_DATA] = The md5 hash of the dataframe used in the session
        [HASH_OF_THE_PARAMETERS] = The md5 hash of the parameters used when API method is called. F.e. when the rule learning method is called, the parameters contain a dictionary with the min_support, min_confidence, min_lift, min_length and max_length.

        The session maps stores the file paths of the results of previous runs of methods. The key of the dictionary is the session id, the value is a dictionary that contains the past method calls & corresponding filepaths for the result of those calls.
        """
        cfg.logger.debug("Calling get_session_map")
        unique_storage_id = "Local"
        if dataframe_in_json == "":
            data_to_use = json.loads(request.data)
            unique_storage_id = request.cookies.get("session_flask")
            dataframe_in_json = data_to_use["dataframe_in_json"]

        path = f"storage/{unique_storage_id}/{hashlib.md5(dataframe_in_json.encode('utf-8')).hexdigest()}"
        path_with_file = f"{path}/session_map.json"
        if not os.path.exists(path):
            cfg.logger.debug("Creating new session_map.json in %s", path)
            os.makedirs(path)
            with open(path_with_file, "w+") as f:
                f.write(json.dumps({}))
            return {}
        else:
            with open(path_with_file, "r") as json_file:
                content = json.loads(json_file.read())
                return content


    #  -------------------------------------------------------------------------- 
    #                                 UTILS: PRIVATE METHODS                               
    #  -------------------------------------------------------------------------- 

    def _verify_in_local_storage(
            self,
            md5_to_check: str,
            unique_storage_id,
            md5_of_dataframe,
            seq,
            save_file=True,
    ) -> json:
        """
        Verifies if a json file is in the local storage. If it is, it returns the json file. If it is not, it returns None.
        :param md5_to_check: the md5 hash of the json file to check
        :type str
        :param unique_storage_id: the unique id of the session
        :type str
        :param md5_of_dataframe: the md5 hash of the dataframe used
        :type str
        :param seq: the sequence number of the method call
        :type int
        :param save_file: boolean to indicate if the path of the file should be saved to the session map
        :type bool
        :return: The json file if it is in the local storage, None if it is not.
        :type: json

        An example of what a file looks like:
        {
        "params": the parameters of another method used in this API put in a dictionary (F.e. Giving suggestions based on found rules: {"list_of_rule_string_in_json": "[\"a,b => c\", \"c => e\"]"} )
        "result": the result of another method used in this API, transformed in a json string
        "seq": the sequence number of the method call, used to identify the sequence of method calls and is used to be able to 'go back' to a previous method call}
        """
        # If method returns None -> Was not in storage with specific settings
        list_of_globs = glob.glob(
            f"storage/{unique_storage_id}/{md5_of_dataframe}/*.json"
        )

        for gl in list_of_globs:
            found_md5 = (gl.split("_")[-1]).split(".")[0]
            if md5_to_check == found_md5:
                with open(gl, "r") as json_file:
                    to_return = json.loads(json_file.read())
                if save_file:
                    self._write_to_session_map(
                        unique_storage_id,
                        md5_of_dataframe,
                        gl.split("/")[-1].split("_")[1],
                        seq,
                        gl,
                        True,
                    )
                return to_return["result"]

        return None

    

    def _write_to_session_map(
            self,
            unique_storage_id,
            md5_of_dataframe,
            method_name: str,
            session_id: str,
            file_name_of_results: str,
            is_in_local: bool,
    ):
        """
        Writes the results of a method to the session map. This is a dictionary that contains the fielpaths of results of previous runs of methods.
        These session maps are stored in the ./storage folder.
        When there isn't a session map stored in the ./storage folder for a specific unique storage id, a new session map is created.

        Format of the session map:
        {
        "1":
            {"rules": "storage/[UNIQUE_STORAGE_ID]/[HASH_OF_THE_DATA]/Rule-learning_rules__[HASH_OF_THE_PARAMETERS].json",
            "suggestions": "storage/[HASH_OF_THE_USER]// Rule-learning_suggestions__[HASH_OF_THE_PARAMETERS].json"}
        }

        With:
        [UNIQUE_STORAGE_ID] = When using the API, a unique id is generated for the session. This is stored in a cookie.
        [HASH_OF_THE_DATA] = The md5 hash of the dataframe used in the session
        [HASH_OF_THE_PARAMETERS] = The md5 hash of the parameters used when API method is called. F.e. when the rule learning method is called, the parameters contain a dictionary with the min_support, min_confidence, min_lift, min_length and max_length.

        The session maps stores the file paths of the results of previous runs of methods. The key of the dictionary is the session id, the value is a dictionary that contains the past method calls & corresponding filepaths for the result of those calls.
        :param unique_storage_id: the unique id of the session
        :type str
        :param md5_of_dataframe: the md5 hash of the dataframe used
        :type str
        :param method_name: the name of the method
        :type str
        :param session_id: the session id of the session (used to identify the session and allows users to go back to previous results)
        :type str
        :param file_name_of_results: the filepath to the results of the method
        :type str
        :param is_in_local: boolean to indicate if the method should look first for the results are in the local storage
        :type bool
        :return:
        """
        session_id = str(session_id)
        path = f"storage/{unique_storage_id}/{md5_of_dataframe}/session_map.json"
        # Create file if it doesn't exist
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(json.dumps({}))

        with open(path, "r") as json_file:
            content = json.loads(json_file.read())

        # Check if session_id is present -> else make new one
        if session_id in content:
            if is_in_local:
                # Create new Session ID to back up
                new_id = str(len(content.keys()) + 1)
                new_dict = content[session_id].copy()
                content[new_id] = new_dict
            content[session_id][method_name] = file_name_of_results
        else:
            content[session_id] = {method_name: file_name_of_results}

        cfg.logger.debug("Writing to file %s", path)
        with open(path, "w+") as json_file:
            json_file.write(json.dumps(content))


    def _save_results_to(self, json_string: str, unique_id: str, md5_hash: str, file_name:str):
        """
        Private method: Saves the results of a method in the API to a json file
        :param json_string: The information to save, which is a json string
        :type json
        :param unique_id: the unique id of the session
        :type str
        :param md5_hash: hash of the data used
        :type str
        :param file_name: name of the file
        :type str
        :return: None
        """
        dir_path = f"storage/{unique_id}/{md5_hash}"
        os.makedirs(dir_path, exist_ok=True)

        with open(f"{dir_path}/{file_name}.json", 'w') as outfile:
            outfile.write(json_string)


    #  --------------------------------------------------------------------------
    #                                 DATA CLEANING: PUBLIC API METHODS
    #  --------------------------------------------------------------------------

    # DATACLEANING
    @route("/clean_dataframe_dataprep", methods=["POST"])
    def clean_dataframe_dataprep(
            self, dataframe_in_json="", custom_pipeline=""
    ) -> json:
        """
        This method is used to clean a dataframe using the dataprep library.
        for more information about the dataprep library, see: https://docs.dataprep.ai/user_guide/clean/introduction.html

        The method takes a dataframe in json format and a custom pipeline as input.
        The custom pipeline is a dictionary with the following format:
        custom_pipeline = [
            {"text": [
                    "operator": "<operator_name>",
                    "parameters": {"<parameter_name>": "<parameter_value>"},
                    ]
            },
        ]

        :param dataframe_in_json: the dataframe in json format
        :type json
        :param custom_pipeline: the custom pipeline to use
        :type dict
        :return: the cleaned dataframe in json format

    """
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
            data_to_use = json.loads(request.data)
            dataframe_in_json = data_to_use["dataframe_in_json"]
            custom_pipeline = data_to_use["custom_pipeline"]
        finally:
            # iterate over custom_pipeline:
            dfc = DataFrameCleaner()
            for k, v in custom_pipeline.items():
                if k == "text":
                    df = pd.read_json(dataframe_in_json)
                    df = dfc.clean_text(df=df, column=df.columns[0], pipeline=v).astype(
                        str
                    )
                    return df.to_json()
            # return {}
            # When the pipeline is empty, return the original dataframe
            return dataframe_in_json

    @route("/fuzzy_match_dataprep", methods=["POST"])
    def fuzzy_match_dataprep(
            self,
            dataframe_in_json="",
            col="",
            cluster_method="",
            df_name="",
            ngram="",
            radius="",
            block_size="",
    ) -> json:
        """
        This method is used to perform fuzzy matching on a dataframe using the dataprep library.
        for more information about the dataprep library, see: https://docs.dataprep.ai/user_guide/clean/clean_duplication.html
        :param dataframe_in_json: the dataframe in json format
        :type json
        :param col: the column to perform fuzzy matching on
        :type string
        :param cluster_method: the cluster method to use, possible values are: "fingerprint", "ngram-fingerprint", "phonetic-fingerprint", "levenshtein"
        :type string
        :param df_name: the name of the dataframe
        :type string
        :param ngram: the ngram size to use, only used when cluster_method is "ngram-fingerprint"
        :type int
        :param radius: the radius to use, only used when cluster_method is "levenshtein"
        :type int
        :param block_size: the block size to use, only used when cluster_method is "levenshtein"
        :type int
        :return: Pandas Series in json format consisting of the different clusters that have been found by the fuzzy matching algorithm, using the parameters specified
        fe. ['Banana', 'Banannna', 'BANANA'] could be clustered together
        """
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
            data_to_use = json.loads(request.data)
            dataframe_in_json = data_to_use["dataframe_in_json"]
            col = data_to_use["col"]
            cluster_method = data_to_use["cluster_method"]
            df_name = data_to_use["df_name"]
            ngram = data_to_use["ngram"]
            radius = data_to_use["radius"]
            block_size = data_to_use["block_size"]
        finally:
            fuzzy_matcher = FuzzyMatcher(
                pd.read_json(dataframe_in_json, convert_dates=False),
                col=col,
                df_name=df_name,
                ngram=ngram,
                radius=radius,
                block_size=block_size,
            )
            fuzzy_matcher.cluster(cluster_method=cluster_method)
            return fuzzy_matcher.clusters.to_json()


    @route("/structure_detection", methods=["POST"])
    def structure_detection(
            self, series_in_json: str="", exception_chars: str="", compress: bool=False
    ) -> json:
        '''
        This method is used to detect the structure of a column in a dataframe.
        By default, the values of a column will be analyzed, by changing all
        letters to "X", all numbers to "9" and all other special characters
        will be not regarded in the analysis.
        Additionally, the user can specify exception characters, which will be
        added to the pattern during the analysis. E.g. '-' in a phone number:
        123-456-789 will be analyzed as 999-999-999.
        The user can also specify whether the values should be compressed or not.
        Meaning all multiple consecutive characters in the structure will be
        reduced to a single occurrence of that character.
        E.g. 123-456-789 would have the structure: 999-999-999, but with the
        compress parameter, the structure would be 9-9-9.
        :param series_in_json: A column of a dataframe (a Pandas.Series) in json format
        :type str
        :param exception_chars: the exception characters, which will be used in the
                                pattern during the analysis. When using multiple exception characters,
                                they should be concatenated to each other. 
                                E.g: "," and '.' should be specified as ",."
        :type str
        :param compress: whether the values should be compressed or not.
                         Meaning all subsequent characters in the structure will be
                         reduced to a single occurrence of that character.
                         Is False by default.
        :type bool
        :return: the structure of the column as a pandas series in json format
        :type: json
        '''
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
            data_to_use = json.loads(request.data)
            series_in_json = data_to_use["series_in_json"]
            exception_chars = data_to_use["exception_chars"]
            compress = data_to_use["compress"]
        finally:
            fuzzy_matcher = StructureDetector(
                pd.read_json(
                    series_in_json, typ="series", orient="records", convert_dates=False
                ),
                exception_chars=exception_chars,
                compress=compress,
            ).find_structure()
            return fuzzy_matcher.to_json()

    #  --------------------------------------------------------------------------
    #                                 DEDUPLICATION: PUBLIC API METHODS
    #  --------------------------------------------------------------------------

    @route("/prepare_zingg", methods=["POST"])
    def prepare_zingg(self, dedupe_type_dict="", dedupe_data="") -> json:
        """
        This method is used to prepare the data for the Zingg deduplication algorithm.
        :param dedupe_type_dict:
        :param dedupe_data:
        :return:
        """
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
            data_to_use = json.loads(request.data)
            dedupe_type_dict = data_to_use["dedupe_type_dict"]
            dedupe_data = data_to_use["dedupe_data"]
        finally:
            _ = Zingg(dedupe_type_dict, dedupe_data, unique_storage_id)
            return ""

    @route("/zingg_clear", methods=["POST"])
    def zingg_clear(self) -> json:
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
        finally:
            _ = Zingg.clear_marked_pairs(unique_storage_id)
            return ""

    @route("/run_zingg_phase", methods=["POST"])
    def run_zingg_phase(self, phase="") -> json:
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
            data_to_use = json.loads(request.data)
            phase = data_to_use["phase"]
        finally:
            return json.dumps(Zingg.run_zingg_phase(phase, unique_storage_id))

    @route("/zingg_unmarked_pairs", methods=["GET"])
    def zingg_unmarked_pairs(self) -> json:
        cfg.logger.debug("Calling zingg_unmarked_pairs")
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
        finally:
            return Zingg.get_unmarked_pairs(unique_storage_id).to_json(orient="records")

    @route("/zingg_mark_pairs", methods=["POST"])
    def zingg_mark_pairs(self, marked_df="") -> json:
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
            data_to_use = json.loads(request.data)
            marked_df = data_to_use["marked_df"]
        finally:
            Zingg.mark_pairs(unique_storage_id, pd.read_json(marked_df))
            return ""

    @route("/zingg_get_stats", methods=["GET"])
    def zingg_get_stats(self) -> json:
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
        finally:
            return json.dumps(Zingg.get_stats(unique_storage_id))

    @route("/zingg_get_clusters", methods=["GET"])
    def zingg_get_clusters(self) -> json:
        unique_storage_id = "Local"
        try:
            unique_storage_id = request.cookies.get("session_flask")
        finally:
            return Zingg.get_clusters(unique_storage_id).to_json(orient="records")





    # RULE LEARNING: LEARN RULES
    @route("/get_all_column_rules_from_df_and_config", methods=["GET", "POST"])
    def get_all_column_rules_from_df_and_config(
            self, dataframe_in_json="", rule_finding_config_in_json="", seq=""
    ) -> json:

        unique_storage_id = "Local"

        try:
            data_to_use = json.loads(request.data)
            unique_storage_id = request.cookies.get("session_flask")
            dataframe_in_json = data_to_use["dataframe_in_json"]
            rule_finding_config_in_json = data_to_use["rule_finding_config_in_json"]
            if "seq" not in data_to_use:
                seq = ""
            else:
                seq = data_to_use["seq"]
        finally:

            cfg.logger.debug("Going to check local storage for results...")

            # VERIFY IF IN LOCAL STORAGE:
            md5_of_dataframe = hashlib.md5(
                dataframe_in_json.encode("utf-8")
            ).hexdigest()
            md5_of_hash = hashlib.md5(
                rule_finding_config_in_json.encode("utf-8")
            ).hexdigest()

            result_in_local_storage = self._verify_in_local_storage(
                md5_to_check=hashlib.md5(
                    rule_finding_config_in_json.encode("utf-8")
                ).hexdigest(),
                unique_storage_id=unique_storage_id,
                md5_of_dataframe=md5_of_dataframe,
                seq=seq,
            )
            if result_in_local_storage is not None:
                cfg.logger.debug("Found results in local storage! Returning them...")
                return json.dumps(result_in_local_storage)

            # COMPUTE RESULTS
            rfc = RuleFindingConfig.create_from_json(rule_finding_config_in_json)
            df = pd.read_json(dataframe_in_json)

            # Drop the columns that are not needed for the rule finding
            df = df[rfc.cols_to_use].astype(str)

            df_ohe = self.data_prepper.transform_data_frame_to_ohe(
                df, drop_nan=False
            )
            self.rule_mediator = RuleMediator(original_df=df, df_ohe=df_ohe)
            self.rule_mediator.create_column_rules_from_clean_dataframe(
                rule_length=rfc.rule_length,
                confidence=rfc.confidence,
                speed=rfc.speed,
                quality=rfc.quality,
                abs_min_support=rfc.abs_min_support,
                g3_threshold=rfc.g3_threshold,
                fi_threshold=rfc.fi_threshold,
                pyro = rfc.pyro,
            )

            result = {
                k: v.parse_self_to_view().to_json()
                for (k, v) in self.rule_mediator.get_all_column_rules().items()
            }

            # SAVE RESULTS
            parsed_date_time = ""
            file_name = f"Rule-learning_rules_{parsed_date_time}_{md5_of_hash}"
            file_path = (
                f"storage/{unique_storage_id}/{md5_of_dataframe}/{file_name}.json"
            )
            self._save_results_to(
                unique_id=unique_storage_id,
                md5_hash=md5_of_dataframe,
                json_string=json.dumps(
                {
                    "result": result,
                    "params": {
                        "rule_finding_config_in_json": rule_finding_config_in_json
                    },
                }
            ),
                file_name=file_name,
            )

            self._write_to_session_map(
                unique_storage_id, md5_of_dataframe, "rules", seq, file_path, False
            )

            # RETURN RESULTS
            return json.dumps(result)

    @route("/get_column_rules_from_strings", methods=["GET", "POST"])
    def get_column_rules_from_strings(self, dataframe_in_json="", list_of_rule_string=""):
        if dataframe_in_json == "" and list_of_rule_string == "":
            data_to_use = json.loads(request.data)
            dataframe_in_json = data_to_use["dataframe_in_json"]
            list_of_rule_string = data_to_use["list_of_rule_string"]

        df = pd.read_json(dataframe_in_json)
        df_to_use = df.astype(str)
        df_OHE = self.data_prepper.transform_data_frame_to_ohe(
            df_to_use, drop_nan=False
        )
        self.rule_mediator = RuleMediator(original_df=df_to_use, df_ohe=df_OHE)
        tmp_dict = {k: self.rule_mediator.get_column_rule_from_string(rule_string=k)
            .parse_self_to_view().to_json()
             for k in list_of_rule_string}
        return json.dumps(tmp_dict)

    @route("/recalculate_column_rules", methods=["GET", "POST"])
    def recalculate_column_rules(
            self,
            old_df_in_json="",
            new_df_in_json="",
            rule_finding_config_in_json="",
            affected_columns="",
    ):
        # Check if remote or local
        unique_storage_id = "Local"
        try:
            data_to_use = json.loads(request.data)
            unique_storage_id = request.cookies.get("session_flask")
            old_df_in_json = data_to_use["old_dataframe_in_json"]
            new_df_in_json = data_to_use["new_dataframe_in_json"]
            rule_finding_config_in_json = data_to_use["rule_finding_config_in_json"]
            affected_columns = data_to_use["affected_columns"]
        finally:
            md5_of_old_dataframe = hashlib.md5(old_df_in_json.encode("utf-8")).hexdigest()
            md5_of_new_dataframe = hashlib.md5(new_df_in_json.encode("utf-8")).hexdigest()
            md5_of_config = hashlib.md5(
                rule_finding_config_in_json.encode("utf-8")
            ).hexdigest()

            # Haal het resultaat op uit de juiste file -> Deze dictionary zijn de oude gevonden column_rules.
            dict_of_column_rules = self._verify_in_local_storage(
                md5_to_check=md5_of_config,
                md5_of_dataframe=md5_of_old_dataframe,
                unique_storage_id=unique_storage_id,
                seq="",
                save_file=False,
            )


            # Herbereken de column_rules op basis van de affected columns.
            list_of_affected_rule_strings = []
            if dict_of_column_rules is not None:
                for k in dict_of_column_rules.keys():

                    # Check if affected columns are in the rule_string
                    af = json.loads(affected_columns)
                    for e in af:
                        if e in k.split(" => ")[1] or e in k.split(" => ")[0].split(','):
                            list_of_affected_rule_strings.append(k)

                list_of_affected_rule_strings = list(set(list_of_affected_rule_strings))
                        
                new_column_rules_dict = json.loads(self.get_column_rules_from_strings(
                                dataframe_in_json=new_df_in_json, list_of_rule_string=list_of_affected_rule_strings
                            ))

                for k,v in new_column_rules_dict.items():
                    dict_of_column_rules[k] = v


            # Schrijf aanpassingen weg naar de schijf
            parsed_date_time = ""
            file_name = f"Rule-learning_rules_{parsed_date_time}_{md5_of_config}"
            file_path = (
                f"storage/{unique_storage_id}/{md5_of_new_dataframe}/{file_name}.json"
            )
            self._save_results_to(
                unique_id=unique_storage_id,
                md5_hash=md5_of_new_dataframe,
                json_string=json.dumps(
                {
                    "result": dict_of_column_rules,
                    "params": {"rule_finding_config_in_json": rule_finding_config_in_json},
                }
            ),
                file_name=file_name,
            )

            # Houd bij in de session map waar de regels zijn opgeslagen
            self._write_to_session_map(
                unique_storage_id=unique_storage_id,
                md5_of_dataframe=md5_of_new_dataframe,
                method_name="rules",
                session_id="1",
                file_name_of_results=file_path,
                is_in_local=False,
            )
            return ""

    @route("/add_rule_to_local_storage", methods=["GET", "POST"])
    def add_rule_to_local_storage(
            self,
            dataframe_in_json="",
            new_rule="",
            rule_finding_config_in_json="",
            seq="",
    ):
        # Check if remote or local
        unique_storage_id = "Local"
        try:
            data_to_use = json.loads(request.data)
            unique_storage_id = request.cookies.get("session_flask")
            dataframe_in_json = data_to_use["dataframe_in_json"]
            new_rule = data_to_use["new_rule"]
            rule_finding_config_in_json = data_to_use["rule_finding_config_in_json"]
            seq = data_to_use["seq"]
        finally:
            md5_of_dataframe = hashlib.md5(dataframe_in_json.encode("utf-8")).hexdigest()
            md5_of_config = hashlib.md5(
                rule_finding_config_in_json.encode("utf-8")
            ).hexdigest()

            # Haal het resultaat op uit de juiste file -> Deze dictionary zijn de oude gevonden column_rules.
            dict_of_column_rules = self._verify_in_local_storage(
                md5_to_check=md5_of_config,
                md5_of_dataframe=md5_of_dataframe,
                unique_storage_id=unique_storage_id,
                seq=seq,
                save_file=False,
            )

            new_rule_object = ColumnRuleView.parse_from_json(new_rule)
            # Voeg de nieuwe rule toe aan de dictionary
            dict_of_column_rules[new_rule_object.rule_string] = new_rule


            # Schrijf aanpassingen weg naar de schijf
            parsed_date_time = ""
            file_name = f"Rule-learning_rules_{parsed_date_time}_{md5_of_config}"
            file_path = (
                f"storage/{unique_storage_id}/{md5_of_dataframe}/{file_name}.json"
            )
            self._save_results_to(
                unique_id=unique_storage_id,
                md5_hash=md5_of_dataframe,
                json_string=json.dumps(
                {
                    "result": dict_of_column_rules,
                    "params": {"rule_finding_config_in_json": rule_finding_config_in_json},
                }
            ),
                file_name=file_name,
            )

            # Houd bij in de session map waar de regels zijn opgeslagen
            self._write_to_session_map(
                unique_storage_id=unique_storage_id,
                md5_of_dataframe=md5_of_dataframe,
                method_name="rules",
                session_id=seq,
                file_name_of_results=file_path,
                is_in_local=False,
            )
            return ""
        
    # RULE LEARNING: GIVE SUGGESTIONS
    @route("/get_suggestions_given_dataframe_and_column_rules", methods=["POST"])
    def get_suggestions_given_dataframe_and_column_rules(
            self, dataframe_in_json="", list_of_rule_string_in_json="", seq=""
    ) -> json:
        # LOAD PARAMS
        unique_storage_id = "Local"
        if dataframe_in_json == "" and list_of_rule_string_in_json == "":
            data_to_use = json.loads(request.data)
            unique_storage_id = request.cookies.get("session_flask")
            dataframe_in_json = data_to_use["dataframe_in_json"]
            list_of_rule_string_in_json = data_to_use["list_of_rule_string_in_json"]
            if "seq" not in data_to_use:
                seq = ""
            else:
                seq = data_to_use["seq"]

        # VERIFY IF IN LOCAL STORAGE:
        md5_of_dataframe = hashlib.md5(dataframe_in_json.encode("utf-8")).hexdigest()
        result_in_local_storage = self._verify_in_local_storage(
            hashlib.md5(list_of_rule_string_in_json.encode("utf-8")).hexdigest(),
            unique_storage_id,
            md5_of_dataframe,
            seq,
        )
        if result_in_local_storage is not None:
            return json.dumps(result_in_local_storage)

        # COMPUTE RESULTS
        list_of_rule_string = json.loads(list_of_rule_string_in_json)
        df = pd.read_json(dataframe_in_json)
        df_to_use = df.astype(str)
        df_OHE = self.data_prepper.transform_data_frame_to_ohe(
            df_to_use, drop_nan=False
        )
        self.rule_mediator = RuleMediator(original_df=df_to_use, df_ohe=df_OHE)

        column_rules = []
        for rs in list_of_rule_string:
            column_rules.append(
                self.rule_mediator.get_column_rule_from_string(rule_string=rs)
            )
        self.suggestion_finder = SuggestionFinder(
            column_rules=column_rules, original_df=df_to_use
        )
        df_rows_with_errors = self.suggestion_finder.df_errors_.drop(
            ["RULESTRING", "FOUND_CON", "SUGGEST_CON"], axis=1
        ).drop_duplicates()
        result = self.suggestion_finder.highest_scoring_suggestion(
            df_rows_with_errors
        ).to_json()
        save_dump = json.dumps(
            {
                "result": result,
                "params": {"list_of_rule_string_in_json": list_of_rule_string_in_json},
                "seq": seq,
            }
        )

        # SAVE RESULTS
        parsed_date_time = ""
        file_name = f"Rule-learning_suggestions_{parsed_date_time}_{hashlib.md5(list_of_rule_string_in_json.encode('utf-8')).hexdigest()}"
        file_path = f"storage/{unique_storage_id}/{md5_of_dataframe}/{file_name}.json"
        self._save_results_to(
            unique_id=unique_storage_id,
            md5_hash=hashlib.md5(dataframe_in_json.encode("utf-8")).hexdigest(),
            json_string=save_dump,
            file_name=file_name,
        )
        self._write_to_session_map(
            unique_storage_id, md5_of_dataframe, "suggestions", seq, file_path, False
        )

        # RETURN RESULTS
        return json.dumps(result)

    # DATA EXTRACTION
    @route("/perform_data_extraction_clustering", methods=["POST"])
    def perform_data_extraction_clustering(
            self, config_dict="", original_df="", df_to_cluster="") -> json:
        """
        this method is called when the user wants to perform data extraction clustering, and already knows the 'best' parameters to use for the clustering

        :param config_dict: the parameters for the clustering method in a dict format. The dictioanry should be formatted as follows:
        {
            "chosen_column": "XXXX",
            "chosen_type": 'categorical' or 'numerical',
            "chosen_algorithm": 'K-means' or 'hdbscan',
            "range_iteration_lower': 1,
            "range_iteration_upper": 10,
            "number_of_scores': 5
        }
        :type: dict
        :param original_df: the original dataframe that should be clustered
        :type: pandas.DataFrame
        :param df_to_cluster: the dataframe that should be clustered, this can either be the original dataframe, or a dataframe that has been preprocessed (For example, has undergone PCA-transformation)
        :type: pandas.DataFrame
        :return:
        """

        try:
            data_to_use = json.loads(request.data)
            config_dict = data_to_use["config_dict"]
            original_df = pd.read_json(data_to_use["original_df"])
            df_to_cluster = pd.read_json(data_to_use["df_to_cluster"])
        finally:
            result = self.data_extractor.perform_data_extraction_clustering(
                config_dict=config_dict, df_to_cluster=df_to_cluster, original_df=original_df
            )
            # RETURN RESULTS
            return result.to_json()

    @route("/calculate_data_extraction_evaluation_scores", methods=["POST"])
    def calculate_data_extraction_evaluation_scores(
            self, config_dict="", df_chosen_column="") -> json:
        """
        method to calculate the evaluation scores for the data extraction, given the config dict and the chosen column.
        The data extration proces is in essence a clustering process. The evaluation scores are for different parameters
        of for a clustering method. This method calculates the evaluation scores and returns them in a json format.
        The different evaluation scores are:
        - db_index: the davies_bouldin_score for the clustering method
        - ch_index: the calinski_harabasz_score for the clustering method
        - avg_silhouette: the silhouette_score for the clustering method
        - inertia: the inertia for the clustering method (Only for K-means)
        The evaluation scores are calculated for a range of iterations of the clustering method. The dict that is returned
        is formatted as follows { number_of_clusters : {SCORES) } F.e.
        F.e.
        {
         5: {
            "db_index": 0.76,
            "ch_index": 500,
            "avg_silhouette": 0.54,
            "inertia": 400
            },

        8: {
            "db_index": 0.76,
            "ch_index": 500,
            "avg_silhouette": 0.54,
            "inertia": 400
            },

        etc.

        }
        :param config_dict: the parameters for the clustering method in a dict format. The dictioanry should be formatted as follows:
        {
            "chosen_column": "XXXX",
            "chosen_type": 'categorical' or 'numerical',
            "chosen_algorithm": 'K-means' or 'hdbscan',
            "range_iteration_lower': 1,
            "range_iteration_upper": 10,
            "number_of_scores': 5
        }
        :type: dict
        :param df_chosen_column: one specific column from the dataset that is chosen to be clustered
        :type: pandas.Series
        :return: a json object with the evaluation scores for the clustering method
        """

        try:
            data_to_use = json.loads(request.data)
            config_dict = data_to_use["config_dict"]
            df_chosen_column = pd.Series(json.loads(data_to_use["df_chosen_column"]))
        finally:
            result = self.data_extractor.calculate_data_extraction_evaluation_scores(config_dict, df_chosen_column)
            # RETURN RESULTS
            return json.dumps(result)