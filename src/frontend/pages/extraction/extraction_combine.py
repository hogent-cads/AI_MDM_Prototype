import streamlit as st
import pandas as pd
import streamlit as st
from hdbscan import HDBSCAN
from sklearn.cluster import MiniBatchKMeans

from src.frontend.enums import Variables


class DataExtractorCombinePage:
    def __init__(self, canvas, handler):
        self.canvas = canvas
        self.handler = handler

    def show(self):
        with self.canvas.container():
            st.header("Combine")

            # Perform extraction with final config
            if st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_ALGORITHM] == "K-means":
                # Create a KMeans instance with k clusters: model
                kmeans = MiniBatchKMeans(
                    n_clusters=st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_PARAM])
                # Then fit the model to your data using the fit method
                model = kmeans.fit_predict(st.session_state[Variables.DE_CLUSTER_DF])

            if st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_ALGORITHM] == "HDBSCAN":
                # Create a HDBSCAN instance with k clusters: model
                hdbscan = HDBSCAN(
                    min_cluster_size=st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_PARAM])
                # Then fit the model to your data using the fit method
                model = hdbscan.fit_predict(st.session_state[Variables.DE_CLUSTER_DF])

            # Determine the cluster labels of new_points: labels
            # group by cluster on the index of the dataframe

            tmp = st.session_state[Variables.SB_LOADED_DATAFRAME][
                st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]].to_frame()
            tmp = tmp.assign(Cluster=model)

            if st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_TYPE] == "Categorical":
                mode_values_df = tmp.groupby("Cluster").agg({st.session_state[Variables.DE_FINAL_CONFIG][
                                                                 Variables.DE_FINAL_CONFIG_COLUMN]: lambda x:
                x.value_counts().index[0]})
            else:
                # Determine min and max values of each cluster
                min_values_df = tmp.groupby("Cluster").agg(
                    {st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]: "min"})
                max_values_df = tmp.groupby("Cluster").agg(
                    {st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]: "max"})
                # Create new column 'range' with the difference between max and min values
                min_values_df = min_values_df.rename(
                    columns={st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]: "min"})
                max_values_df = max_values_df.rename(
                    columns={st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]: "max"})
                range_values_df = pd.concat([min_values_df, max_values_df], axis=1)
                mode_values_df = range_values_df.apply(lambda x: f"[{x['min']} - {x['max']}]", axis=1)

            tmp = tmp.groupby("Cluster").agg(
                {st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]: "unique"})
            tmp = tmp.rename(
                columns={st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]: "Values"})
            tmp["Cluster"] = mode_values_df

            if 'tmp' not in st.session_state:
                st.session_state['tmp'] = tmp

            merge_dict = {}

            for e in range(len(st.session_state['tmp']["Cluster"])):
                value_to_replace = st.session_state['tmp']["Cluster"][e]
                with st.expander(label=f"Cluster #{e}", expanded=True if e == 0 else False):
                    col1AA, col2AA = st.columns([2, 1])
                    with col1AA:
                        values = st.multiselect(label=f"Current Values: ", options=st.session_state['tmp']["Values"][e],
                                                default=st.session_state['tmp']["Values"][e].tolist(),
                                                key=f"multiselect_{e}")
                    with col2AA:
                        st.session_state['tmp']["Cluster"][e] = st.text_input(label=f"New Value: ",
                                                                              value=value_to_replace,
                                                                              key=f"text_input_{e}", )

                merge_dict[st.session_state['tmp']["Cluster"][e]] = values

            col1BBB, col2BBB, col3BBB, _ = st.columns([1, 1, 1, 1])
            with col2BBB:
                st.write("")
                st.write("")
                create_new_flag = st.checkbox(label="Create new column")
            with col3BBB:
                if create_new_flag:
                    new_col_name = st.text_input(label="New column name: ",
                                                 value=f"{st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]}_combined")
            with col1BBB:
                st.write("")
                st.write("")
                if st.button(label="Combine clusters"):
                    if create_new_flag:
                        st.session_state[Variables.SB_LOADED_DATAFRAME][new_col_name] = \
                        st.session_state[Variables.SB_LOADED_DATAFRAME][st.session_state[Variables.DE_FINAL_CONFIG][
                            Variables.DE_FINAL_CONFIG_COLUMN]].copy().astype(str)
                    for key, value in merge_dict.items():
                        for v in value:
                            if not create_new_flag:
                                st.session_state[Variables.SB_LOADED_DATAFRAME][
                                    st.session_state[Variables.DE_FINAL_CONFIG][Variables.DE_FINAL_CONFIG_COLUMN]] = \
                                st.session_state[Variables.SB_LOADED_DATAFRAME][
                                    st.session_state[Variables.DE_FINAL_CONFIG][
                                        Variables.DE_FINAL_CONFIG_COLUMN]].replace(v, key)
                            else:
                                st.session_state[Variables.SB_LOADED_DATAFRAME][new_col_name] = \
                                st.session_state[Variables.SB_LOADED_DATAFRAME][new_col_name].replace(str(v), key)

                    st.session_state[Variables.GB_CURRENT_STATE] = None
                    st.experimental_rerun()
