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
                  ["java"]
                + ["-classpath"]
                + ["./external/metanome-utils/pyro-distro-1.0-SNAPSHOT-distro.jar:./external/metanome-utils/metanome-cli-1.1.0.jar"]
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
