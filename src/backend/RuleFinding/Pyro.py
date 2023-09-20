import os
from pathlib import Path
import hashlib
from subprocess import Popen, PIPE, STDOUT
import subprocess
import platform
import shutil
import json

import pandas as pd
import pyarrow.parquet as pq

import config as cfg

class Pyro:
    def __init__(
        self,  
    ) -> None:
        pass

    @staticmethod
    def read_in_results(path, df2):
        # df2 = original data
        with open(path, 'r') as f:
            data = f.readlines()
            all_data = [json.loads(line) for line in data]

        df = pd.DataFrame(columns=['list_of_determinants', 'dependant'])

        for idx, e in enumerate(all_data):
            list_of_dicts = e["determinant"]["columnIdentifiers"]
            # extract all 'columnIdentifier' values and place them in a list
            list_of_determinants = [d['columnIdentifier'] for d in list_of_dicts]
            dependant = e["dependant"]["columnIdentifier"]
            df.loc[idx] = [list_of_determinants, dependant]


        # create a dictionary as follows:
        # {'column1': column0, 'column2': column1, ...}
        col_dict = {}
        for idx, colname in enumerate(df2.columns):
            col_dict['column'+str(idx+1)] = str(df2.columns[idx])

        # Transform the column numbers to column names based on col_dict
        for idx, row in df.iterrows():
            for idx2, col in enumerate(row['list_of_determinants']):
                df.at[idx, 'list_of_determinants'][idx2] = col_dict[col]
            df.at[idx, 'dependant'] = col_dict[row['dependant']]
        
        # Create a list of strings of the form "A,B => C"
        rule_strings = []
        for idx, row in df.iterrows():
            rule_strings.append(','.join(row['list_of_determinants']) + ' => ' + row['dependant'])

        return rule_strings

    @staticmethod
    def run_pyro(modelID, df2, ):
        # Create an input file for Pyro
        
        Path(f"storage/{modelID}/input_dir").mkdir(parents=True, exist_ok=True)
        df2.to_csv(f"storage/{modelID}/input_dir/input.csv", index=False)

        if os.path.exists(f"./results"):
            shutil.rmtree(f"./results")

        system = platform.system()
        if system == "Windows":
            cmd = (
                ["java"]
                + ["-classpath"]
                + ["./external/metanome-utils/pyro-distro-1.0-SNAPSHOT-distro.jar;./external/metanome-utils/metanome-cli-1.1.0.jar"]
                + ["de.metanome.cli.App"]
                + ["--algorithm"]
                + ["de.hpi.isg.pyro.algorithms.Pyro"]
                + ["--files"]
                + [f"./storage/{modelID}/input_dir/input.csv"]
                + ["--file-key"]
                + ["inputFile "]
                + ["--separator"]
                + ['","']
            )

            process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
            _, _ = process.communicate()

        elif system == "Linux":
            cmd = (
                ["/bin/bash"]
                + ["java"]
                + ["-classpath"]
                + ["./external/metanome-utils/pyro-distro-1.0-SNAPSHOT-distro.jar;./external/metanome-utils/metanome-cli-1.1.0.jar"]
                + ["de.metanome.cli.App"]
                + ["--algorithm"]
                + ["de.hpi.isg.pyro.algorithms.Pyro"]
                + ["--files"]
                + [f"./storage/{modelID}/input_dir/input.csv"]
                + ["--file-key"]
                + ["inputFile "]
                + ["--separator"]
                + ['","']
            )
            process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
            output, err = process.communicate()
            cfg.logger.debug(output.decode("utf-8") if output is not None else "")
            cfg.logger.debug(err.decode("utf-8") if err is not None else "")
        else:
            raise ValueError("Unsupported OS")
        

        # Read in the data from the output file that ends with .fds
        path = os.path.join("./results", [f for f in os.listdir("./results") if f.endswith("_fds")][0])
        with open(path, 'r') as f:
            all_data = f.readlines()
            all_data = [json.loads(line) for line in all_data]

        df = pd.DataFrame(columns=['list_of_determinants', 'dependant'])

        for idx, e in enumerate(all_data):
            list_of_dicts = e["determinant"]["columnIdentifiers"]
            # extract all 'columnIdentifier' values and place them in a list
            list_of_determinants = [d['columnIdentifier'] for d in list_of_dicts]
            dependant = e["dependant"]["columnIdentifier"]
            df.loc[idx] = [list_of_determinants, dependant]

        col_dict = {}
        for idx, colname in enumerate(df2.columns):
            col_dict['column'+str(idx+1)] = str(df2.columns[idx])

        # Transform the column numbers to column names based on col_dict
        for idx, row in df.iterrows():
            for idx2, col in enumerate(row['list_of_determinants']):
                df.at[idx, 'list_of_determinants'][idx2] = col_dict[col]
            df.at[idx, 'dependant'] = col_dict[row['dependant']]

        # Create a list of strings of the form "A,B => C"
        rule_strings = []
        for idx, row in df.iterrows():
            rule_strings.append(','.join(row['list_of_determinants']) + ' => ' + row['dependant'])
            
        return rule_strings

    @staticmethod
    def _read_parquet_schema_df(uri: str) -> pd.DataFrame:
        """Return a Pandas dataframe corresponding to the schema of a local URI of a parquet file.

        The returned dataframe has the columns: column, pa_dtype
        """
        # Ref: https://stackoverflow.com/a/64288036/
        schema = pq.read_schema(uri, memory_map=True)
        schema = pd.DataFrame(
            (
                {"column": name, "pa_dtype": str(pa_dtype)}
                for name, pa_dtype in zip(schema.names, schema.types)
            )
        )
        schema = schema.reindex(
            columns=["column", "pa_dtype"], fill_value=pd.NA
        )  # Ensures columns in case the parquet file has an empty dataframe.
        return schema

    @staticmethod
    def get_unmarked_pairs(modelID):
        # Go to directory and read in parquet files
        dir = f"storage/{modelID}/models/{modelID}/trainingData/unmarked"

        files = os.listdir(dir)
        files = [os.path.join(dir, f) for f in files if f.endswith(".parquet")]

        return pd.concat([pd.read_parquet(f) for f in files])

    @staticmethod
    def clear_marked_pairs(modelID):
        # remove existing marked pairs
        if os.path.exists(f"storage/{modelID}/models/{modelID}/trainingData/marked"):
            shutil.rmtree(f"storage/{modelID}/models/{modelID}/trainingData/marked")

    @staticmethod
    def mark_pairs(modelID, dataframe):
        dir = f"storage/{modelID}/models/{modelID}/trainingData/marked"
        Path(dir).mkdir(parents=True, exist_ok=True)

        for z_cluster_id, z_cluster_df in dataframe.groupby("z_cluster"):
            # create md5 hash of z_cluster_id
            z_cluster_id = hashlib.md5(z_cluster_id.encode()).hexdigest()
            label = z_cluster_df["z_isMatch"].iloc[0]

            # Make all String:
            z_cluster_df = z_cluster_df.astype(str)

            # Set the type of the columns to the same as in the unmarked pairs.
            z_cluster_df["z_zid"] = z_cluster_df["z_zid"].astype("int64")
            # z_cluster_df["z_cluster"] = z_cluster_df["z_cluster"].astype("string")
            z_cluster_df["z_prediction"] = z_cluster_df["z_prediction"].astype("double")
            z_cluster_df["z_score"] = z_cluster_df["z_score"].astype("double")
            z_cluster_df["z_isMatch"] = z_cluster_df["z_isMatch"].astype("int32")
            # z_cluster_df["z_score"] = z_cluster_df["z_score"].astype("string")

            # save to parquet file
            z_cluster_df.to_parquet(
                f"{dir}/{label}{z_cluster_id}.parquet",
                index=False,
            )
            tmp = Zingg._read_parquet_schema_df(f"{dir}/{label}{z_cluster_id}.parquet")
            cfg.logger.debug("Saved %s.parquet", z_cluster_id)

    @staticmethod
    def get_stats(modelID):
        # Go to directory and read in parquet files
        dir = f"storage/{modelID}/models/{modelID}/trainingData/marked"
        # check if directory exists
        if not os.path.exists(dir):
            return {"match_files": 0, "no_match_files": 0, "unsure_files": 0}
        files = os.listdir(dir)

        match_files = len(
            [f for f in files if f.startswith("1") & f.endswith(".parquet")]
        )
        no_match_files = len(
            [f for f in files if f.startswith("0") & f.endswith(".parquet")]
        )
        unsure_files = len(
            [f for f in files if f.startswith("2") & f.endswith(".parquet")]
        )
        return {
            "match_files": match_files,
            "no_match_files": no_match_files,
            "unsure_files": unsure_files,
        }

    @staticmethod
    def get_clusters(modelID):
        output_dir = f"storage/{modelID}/output_dir"
        files = os.listdir(output_dir)
        files = [os.path.join(output_dir, f) for f in files if f.endswith(".parquet")]
        combined_df = pd.concat([pd.read_parquet(f) for f in files])
        # Delete the row with z_cluster == 0
        return combined_df[combined_df["z_cluster"] != 0]