import math

import plotly.graph_objects as go
import streamlit as st
from hdbscan import HDBSCAN
from kneed import KneeLocator
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import davies_bouldin_score, calinski_harabasz_score, silhouette_score

from src.frontend.enums import Variables


class DataExtractorResultsPage:
    def __init__(self, canvas, handler):
        self.canvas = canvas
        self.handler = handler

    def find_knee(self, x, y, S, curve, direction, online, interp_method, polynomial_degree):
        kl = KneeLocator(
            x=x,
            y=y,
            S=S,
            curve=curve,
            direction=direction,
            online=online,
            interp_method=interp_method,
            polynomial_degree=polynomial_degree,
        )
        return kl

    def plot_figure(self, x, y, kl, all_knees):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line=dict(color="cornflowerblue", width=6),
                name="input data",
            )
        )
        if all_knees:
            fig.add_trace(
                go.Scatter(
                    x=sorted(list(kl.all_knees)),
                    y=list(kl.all_knees_y),
                    mode="markers",
                    marker=dict(
                        color="orange",
                        size=12,
                        line=dict(width=1, color="DarkSlateGrey"),
                    ),
                    marker_symbol="circle",
                    name="potential knee",
                )
            )
        fig.add_trace(
            go.Scatter(
                x=[kl.knee],
                y=[kl.knee_y],
                mode="markers",
                marker=dict(
                    color="orangered",
                    size=16,
                    line=dict(width=1, color="DarkSlateGrey"),
                ),
                marker_symbol="x",
                name="knee point",
            )
        )
        fig.update_layout(
            title="Knee/Elbow(s) in Your Data",
            title_x=0.5,
            xaxis_title="x",
            yaxis_title="y",
        )
        fig.update_layout(
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor="rgb(204, 204, 204)",
                linewidth=4,
                ticks="outside",
                tickfont=dict(
                    family="Arial",
                    size=18,
                    color="rgb(82, 82, 82)",
                ),
            ),
            yaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor="rgb(204, 204, 204)",
                linewidth=4,
                ticks="outside",
                tickfont=dict(
                    family="Arial",
                    size=18,
                    color="rgb(82, 82, 82)",
                ),
            ),
            showlegend=True,
            plot_bgcolor="white",
        )
        return fig

    def show(self):
        with self.canvas.container():

            try:
                centers = list(
                    range(st.session_state[Variables.DE_CONFIG]['range_iteration_lower'],
                          st.session_state[Variables.DE_CONFIG]['range_iteration_upper'],
                          st.session_state[Variables.DE_CONFIG]['range_iteration_upper'] //
                          st.session_state[Variables.DE_CONFIG]['number_of_scores']))

                if st.session_state[Variables.DE_STORED_CONFIG] != st.session_state[Variables.DE_CONFIG]:

                    if st.session_state[Variables.DE_CONFIG]['chosen_type'] == "Categorical":
                        # If categorical, we need to extract the tfidf vectors and use PCA to reduce the dimensionality
                        tfidf_vectorizer_vectors = self.extract_tfidf_vectors(
                            st.session_state[Variables.DE_CONFIG]['chosen_column'])
                        st.session_state[Variables.DE_CLUSTER_DF] = self.perform_pca(tfidf_vectorizer_vectors, 0.95)
                    else:
                        # Numerical
                        st.session_state[Variables.DE_CLUSTER_DF] = st.session_state[Variables.SB_LOADED_DATAFRAME][
                            st.session_state[Variables.DE_CONFIG]['chosen_column']].astype(float).to_frame()

                    # K-means
                    if st.session_state[Variables.DE_CONFIG]['chosen_algorithm'] == "K-means":
                        scores = {}
                        for center in centers:
                            print(f"calculating scores for: {center}")
                            scores[center] = self.get_cluster_scores_kmeans(st.session_state[Variables.DE_CLUSTER_DF],
                                                                            center)
                        st.session_state[Variables.DE_SCORES] = scores

                        # HDBSCAN
                    if st.session_state[Variables.DE_CONFIG]['chosen_algorithm'] == "HDBSCAN":
                        scores = {}
                        for min_sample in centers:
                            print(f"calculating scores for: {min_sample}")
                            scores[min_sample] = self.get_cluster_scores_hdbscan(
                                st.session_state[Variables.DE_CLUSTER_DF], min_sample)
                        st.session_state[Variables.DE_SCORES] = scores

                    st.session_state[Variables.DE_STORED_CONFIG] = st.session_state[Variables.DE_CONFIG]

                else:
                    scores = st.session_state[Variables.DE_SCORES]

            except Exception as e:
                st.error(f"Invalid configuration options: {e}")
                st.session_state[Variables.GB_CURRENT_STATE] = None
                return

            st.header("Results:")

            with st.expander(label="Show average Silhouette score", expanded=True):
                st.write('Avg Silhouette')
                st.write(self.plot_figure(x=centers, y=[v['avg_silhouette'] for v in scores.values()],
                                          kl=self.find_knee(x=centers, y=[v['avg_silhouette'] for v in scores.values()],
                                                            S=1.0, curve="concave", direction="increasing",
                                                            online=False,
                                                            interp_method="interp1d", polynomial_degree=3),
                                          all_knees=True))

            with st.expander(label="Show additional information", expanded=False):

                if sum([v['inertia'] for v in scores.values()]) != 0:
                    st.write('Inertia')
                    st.write(self.plot_figure(x=centers, y=[v['inertia'] for v in scores.values()],
                                              kl=self.find_knee(x=centers, y=[v['inertia'] for v in scores.values()],
                                                                S=1.0,
                                                                curve="convex", direction="increasing", online=True,
                                                                interp_method="interp1d", polynomial_degree=3),
                                              all_knees=False))

                st.write('CH Index')
                st.write(self.plot_figure(x=centers, y=[v['ch_index'] for v in scores.values()],
                                          kl=self.find_knee(x=centers, y=[v['ch_index'] for v in scores.values()],
                                                            S=1.0,
                                                            curve="convex", direction="increasing", online=True,
                                                            interp_method="interp1d", polynomial_degree=3),
                                          all_knees=False))

                st.write('DB Index')
                st.write(self.plot_figure(x=centers, y=[v['db_index'] for v in scores.values()],
                                          kl=self.find_knee(x=centers, y=[v['db_index'] for v in scores.values()],
                                                            S=1.0,
                                                            curve="convex", direction="increasing", online=True,
                                                            interp_method="interp1d", polynomial_degree=3),
                                          all_knees=False))

            st.subheader("Continue with the following parameters")
            col_final_params1, col_final_params2, col_final_params3, col_final_params4 = st.columns([1, 1, 1, 1])
            with col_final_params1:
                f_column = st.selectbox(label="Column", options=st.session_state[Variables.SB_LOADED_DATAFRAME].columns,
                                        index=st.session_state[Variables.SB_LOADED_DATAFRAME].columns.get_loc(
                                            st.session_state[Variables.DE_CONFIG]['chosen_column']))
            with col_final_params2:
                f_type = st.selectbox(label="Type", options=["Categorical", "Numeric"],
                                      index=0 if st.session_state[Variables.DE_CONFIG][
                                                     'chosen_type'] == "Categorical" else 1)
            with col_final_params3:
                f_algo = st.selectbox(label="Algorithm", options=["K-means", "HDBSCAN"],
                                      index=0 if st.session_state[Variables.DE_CONFIG][
                                                     'chosen_algorithm'] == "K-means" else 1)
            with col_final_params4:

                # Check if a knee point is found in the avg silhouette score
                knee = self.find_knee(x=centers, y=[v['avg_silhouette'] for v in scores.values()],
                                      S=1.0, curve="concave", direction="increasing", online=False,
                                      interp_method="interp1d", polynomial_degree=3)

                if knee.knee:
                    final_param = knee.knee
                else:
                    final_param = centers[0]

                if st.session_state[Variables.DE_CONFIG]['chosen_algorithm'] == "K-means":
                    f_param = st.number_input(label="Number of clusters", value=final_param)
                else:
                    f_param = st.number_input(label="Min sample", value=final_param)
            if st.button('Apply'):
                st.session_state[Variables.DE_FINAL_CONFIG] = {
                    Variables.DE_FINAL_CONFIG_COLUMN: f_column,
                    Variables.DE_FINAL_CONFIG_TYPE: f_type,
                    Variables.DE_FINAL_CONFIG_ALGORITHM: f_algo,
                    Variables.DE_FINAL_CONFIG_PARAM: f_param
                }
                st.session_state[Variables.GB_CURRENT_STATE] = Variables.ST_DE_COMBINE

    def get_cluster_scores_kmeans(self, cluster_df, center):
        # Create a KMeans instance with k clusters: model
        kmeans = MiniBatchKMeans(n_clusters=center)
        # Then fit the model to your data using the fit method
        model = kmeans.fit_predict(cluster_df)

        # Calculate Davies Bouldin score
        db_index = davies_bouldin_score(cluster_df, model)
        inertia = kmeans.inertia_
        ch_index = calinski_harabasz_score(cluster_df, model)
        avg_silhouette = silhouette_score(cluster_df, model)

        return {
            'db_index': db_index,
            'inertia': inertia,
            'ch_index': ch_index,
            'avg_silhouette': avg_silhouette
        }

    def get_cluster_scores_hdbscan(self, cluster_df, min_sample):
        # Create a HDSCAN instance
        hdbscan = HDBSCAN(min_cluster_size=min_sample)
        # Then fit the model to your data using the fit method
        model = hdbscan.fit_predict(cluster_df)

        # Calculate Davies Bouldin score
        db_index = davies_bouldin_score(cluster_df, model)
        # TODO Change
        inertia = 0
        ch_index = calinski_harabasz_score(cluster_df, model)
        avg_silhouette = silhouette_score(cluster_df, model)

        return {
            'db_index': db_index,
            'inertia': inertia,
            'ch_index': ch_index,
            'avg_silhouette': avg_silhouette
        }

    def perform_pca(self, tfidf_vectorizer_vectors, variance_expl=0.95):
        print(f"total features: {tfidf_vectorizer_vectors.shape[1]}")

        if tfidf_vectorizer_vectors.shape[1] <= 10:
            iteration_step_size = 1
        elif tfidf_vectorizer_vectors.shape[1] <= 100:
            iteration_step_size = 10
        else:
            iteration_step_size = math.floor(tfidf_vectorizer_vectors.shape[1] / 25)

        print(f"iteration step size: {iteration_step_size}")
        # 1570 is the step size for the products.csv dataset
        for comp in range(1, tfidf_vectorizer_vectors.shape[1], iteration_step_size):
            pca = TruncatedSVD(n_components=comp, random_state=42)
            pca.fit(tfidf_vectorizer_vectors)
            comp_check = pca.explained_variance_ratio_
            final_comp = comp
            print(f"size: {comp}, variance: {comp_check.sum()}")
            if comp_check.sum() > variance_expl:
                print(f"final size: {final_comp}, final variance: {comp_check.sum()}")
                break
        Final_PCA = TruncatedSVD(n_components=final_comp, random_state=42)
        Final_PCA.fit(tfidf_vectorizer_vectors)
        cluster_df = Final_PCA.transform(tfidf_vectorizer_vectors)
        # num_comps = comp_check.shape[0]
        # st.write(
        #     f"Using {final_comp} components, we can explain {comp_check.sum()}% of the variability in the original data.")
        return cluster_df

    def extract_tfidf_vectors(self, chosen_column):
        # keuze tussen char of word
        chosen_ngrams = "char"
        # Bepaalde range van ngrams
        chosen_ngram_range = (2, 4)
        try:
            tfidf_vectorizer = TfidfVectorizer(use_idf=True, analyzer=chosen_ngrams, ngram_range=chosen_ngram_range)
            tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(
                st.session_state[Variables.SB_LOADED_DATAFRAME][chosen_column].astype(str).to_list())
            return tfidf_vectorizer_vectors
        except Exception as e:
            chosen_ngram_range = (1, 1)
            tfidf_vectorizer = TfidfVectorizer(use_idf=True, analyzer=chosen_ngrams, ngram_range=chosen_ngram_range)
            tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(
                st.session_state[Variables.SB_LOADED_DATAFRAME][chosen_column].astype(str).to_list())
            return tfidf_vectorizer_vectors
        