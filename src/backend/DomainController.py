import hashlib
import glob
import os
from datetime import datetime

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
from src.backend.HelperFunctions import HelperFunctions
import config as cfg


class DomainController(FlaskView):
    def __init__(self, session_dict={}, app=None) -> None:
        self.session_dict = session_dict
        self.app = app
        self.data_prepper = DataPrepper()
        self.rule_mediator = None
        self.suggestion_finder = None

    # ZINGG METHODS
    @route("/prepare_zingg", methods=["POST"])
    def prepare_zingg(self, dedupe_type_dict="", dedupe_data="") -> json:
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

    # FETCHING OF FILES FOR GUI STATE:
    @route("/fetch_file_from_filepath", methods=["POST"])
    def fetch_file_from_filepath(self, filepath: str = ""):
        if filepath == "":
            data_to_use = json.loads(request.data)
            filepath = data_to_use["filepath"]
        with open(filepath, "r") as json_file:
            content = json_file.read()
        return content

    # VERIFICATION IN LOCAL STORAGE
    def _verify_in_local_storage(
            self,
            md5_to_check: str,
            unique_storage_id,
            md5_of_dataframe,
            seq,
            save_file=True,
    ) -> json:
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

    # METHODS FOR SESSION_MAP
    @route("/get_session_map", methods=["GET", "POST"])
    def get_session_map(self, dataframe_in_json=""):
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

    def _write_to_session_map(
            self,
            unique_storage_id,
            md5_of_dataframe,
            method_name: str,
            session_id: str,
            file_name_of_results: str,
            is_in_local: bool,
    ):
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

    # DATA PERPARATION
    @route("/clean_dataframe", methods=["GET", "POST"])
    def clean_dataframe(self, df, json_string):
        return self.data_prepper.clean_data_frame(df, json_string)

    # DATACLEANING
    # TODO REPLACE
    @route("/clean_dataframe_dataprep", methods=["POST"])
    def clean_dataframe_dataprep(
            self, dataframe_in_json="", custom_pipeline=""
    ) -> json:
        # custom_pipeline = [
        # {"text": [
        #         "operator": "<operator_name>",
        #         "parameters": {"<parameter_name>": "<parameter_value>"},
        #     ]
        # ]
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
            self, series_in_json="", exception_chars="", compress=""
    ) -> json:
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

    # RULE LEARNING
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
                max_potential_confidence=rfc.max_potential_confidence,
                g3_threshold=rfc.g3_threshold,
                fi_threshold=rfc.fi_threshold,
            )

            result = {
                k: v.parse_self_to_view().to_json()
                for (k, v) in self.rule_mediator.get_all_column_rules().items()
            }
            save_dump = json.dumps(
                {
                    "result": result,
                    "params": {
                        "rule_finding_config_in_json": rule_finding_config_in_json
                    },
                }
            )

            # SAVE RESULTS
            parsed_date_time = datetime.now().strftime("%m_%d_%H_%M_%S")
            file_name = f"Rule-learning_rules_{parsed_date_time}_{hashlib.md5(rule_finding_config_in_json.encode('utf-8')).hexdigest()}"
            file_path = (
                f"storage/{unique_storage_id}/{md5_of_dataframe}/{file_name}.json"
            )
            HelperFunctions.save_results_to(
                unique_id=unique_storage_id,
                md5_hash=hashlib.md5(dataframe_in_json.encode("utf-8")).hexdigest(),
                json_string=save_dump,
                file_name=file_name,
            )

            self._write_to_session_map(
                unique_storage_id, md5_of_dataframe, "rules", seq, file_path, False
            )

            # RETURN RESULTS
            return json.dumps(result)

    @route("/get_column_rule_from_string", methods=["GET", "POST"])
    def get_column_rule_from_string(self, dataframe_in_json="", rule_string=""):
        if dataframe_in_json == "" and rule_string == "":
            data_to_use = json.loads(request.data)
            dataframe_in_json = data_to_use["dataframe_in_json"]
            rule_string = data_to_use["rule_string"]

        df = pd.read_json(dataframe_in_json)
        df_to_use = df.astype(str)
        df_OHE = self.data_prepper.transform_data_frame_to_ohe(
            df_to_use, drop_nan=False
        )

        self.rule_mediator = RuleMediator(original_df=df_to_use, df_ohe=df_OHE)
        return (
            self.rule_mediator.get_column_rule_from_string(rule_string=rule_string)
            .parse_self_to_view()
            .to_json()
        )

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
        if (
                old_df_in_json == ""
                and new_df_in_json == ""
                and rule_finding_config_in_json == ""
                and affected_columns == ""
        ):
            data_to_use = json.loads(request.data)
            unique_storage_id = request.cookies.get("session_flask")
            old_df_in_json = data_to_use["old_dataframe_in_json"]
            new_df_in_json = data_to_use["new_dataframe_in_json"]
            rule_finding_config_in_json = data_to_use["rule_finding_config_in_json"]
            affected_columns = data_to_use["affected_columns"]

        md5_of_old_dataframe = hashlib.md5(old_df_in_json.encode("utf-8")).hexdigest()
        md5_of_new_dataframe = hashlib.md5(new_df_in_json.encode("utf-8")).hexdigest()
        md5_of_config = hashlib.md5(
            rule_finding_config_in_json.encode("utf-8")
        ).hexdigest()

        # Haal het resultaat op uit de juiste file -> Deze dictionary zijn de oude gevonden column_rules.
        dict_of_column_rules = self._verify_in_local_storage(
            md5_to_check=md5_of_config,
            md5_of_dataframe=md5_of_old_dataframe,
            # VERY HOT PATCH
            # unique_storage_id='None-'+md5_of_old_dataframe,
            unique_storage_id=unique_storage_id,
            # unique_storage_id=unique_storage_id,
            seq="",
            save_file=False,
        )

        # Pas deze aan: Meest domme manier is om get_column_rule_from_string aan te roepen en op die manier deze te vervangen
        if dict_of_column_rules is not None:
            for k in dict_of_column_rules.keys():
                ks = k.split(" => ")
                ksr = ks[1]
                ksl_list = ks[0].split(",")
                kstotal = [ksr] + ksl_list
                for e in json.loads(affected_columns):
                    if e in kstotal:
                        dict_of_column_rules[k] = self.get_column_rule_from_string(
                            dataframe_in_json=new_df_in_json, rule_string=k
                        )
                        break

        # Maak save_dump
        save_dump = json.dumps(
            {
                "result": dict_of_column_rules,
                "params": {"rule_finding_config_in_json": rule_finding_config_in_json},
            }
        )

        # Schrijf dit weg naar de schijf en pas session map aan.
        parsed_date_time = datetime.now().strftime("%m_%d_%H_%M_%S")
        file_name = f"Rule-learning_rules_{parsed_date_time}_{md5_of_config}"
        file_path = (
            f"storage/{unique_storage_id}/{md5_of_new_dataframe}/{file_name}.json"
        )

        # Schrijf de nieuwe regels weg
        HelperFunctions.save_results_to(
            unique_id=unique_storage_id,
            md5_hash=md5_of_new_dataframe,
            json_string=save_dump,
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

    # SUGGESTIONS
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
        parsed_date_time = datetime.now().strftime("%m_%d_%H_%M_%S")
        file_name = f"Rule-learning_suggestions_{parsed_date_time}_{hashlib.md5(list_of_rule_string_in_json.encode('utf-8')).hexdigest()}"
        file_path = f"storage/{unique_storage_id}/{md5_of_dataframe}/{file_name}.json"
        HelperFunctions.save_results_to(
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

# DomainController.register(app, route_base="/")
