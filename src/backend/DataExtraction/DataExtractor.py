import math
import pandas as pd

from hdbscan import HDBSCAN
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import davies_bouldin_score, calinski_harabasz_score, silhouette_score

from src.frontend.enums import Variables

class DataExtractor:
    def __init__(self) -> None:
        pass

    def _get_cluster_scores_kmeans(self, cluster_df, center):
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

    def _get_cluster_scores_hdbscan(self, cluster_df, min_sample):
        # Create a HDSCAN instance
        hdbscan = HDBSCAN(min_cluster_size=min_sample)
        # Then fit the model to your data using the fit method
        model = hdbscan.fit_predict(cluster_df)

        # Calculate Davies Bouldin score
        db_index = davies_bouldin_score(cluster_df, model)
        inertia = 0
        ch_index = calinski_harabasz_score(cluster_df, model)
        avg_silhouette = silhouette_score(cluster_df, model)

        return {
            'db_index': db_index,
            'inertia': inertia,
            'ch_index': ch_index,
            'avg_silhouette': avg_silhouette
        }

    def _perform_pca(self, tfidf_vectorizer_vectors, variance_expl=0.95):
        print(f"total features: {tfidf_vectorizer_vectors.shape[1]}")

        if tfidf_vectorizer_vectors.shape[1] <= 10:
            iteration_step_size = 1
        elif tfidf_vectorizer_vectors.shape[1] <= 100:
            iteration_step_size = 10
        else:
            iteration_step_size = math.floor(tfidf_vectorizer_vectors.shape[1] / 20)

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
        return pd.DataFrame(cluster_df)

    def _extract_tfidf_vectors(self, df_chosen_column):
        # keuze tussen char of word
        chosen_ngrams = "char"
        # Bepaalde range van ngrams
        chosen_ngram_range = (2, 4)
        try:
            tfidf_vectorizer = TfidfVectorizer(use_idf=True, analyzer=chosen_ngrams, ngram_range=chosen_ngram_range)
            tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(
                df_chosen_column.astype(str).to_list())
            return tfidf_vectorizer_vectors
        except Exception as e:
            chosen_ngram_range = (1, 1)
            tfidf_vectorizer = TfidfVectorizer(use_idf=True, analyzer=chosen_ngrams, ngram_range=chosen_ngram_range)
            tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(
                df_chosen_column.astype(str).to_list())
            return tfidf_vectorizer_vectors

    def perform_data_extraction_clustering(self,config_dict, df_to_cluster, original_df):
        if config_dict[Variables.DE_FINAL_CONFIG_ALGORITHM] == "K-means":
                # Create a KMeans instance with k clusters: model
                kmeans = MiniBatchKMeans(
                    n_clusters=config_dict[Variables.DE_FINAL_CONFIG_PARAM])
                # Then fit the model to your data using the fit method
                model = kmeans.fit_predict(df_to_cluster)

        if config_dict[Variables.DE_FINAL_CONFIG_ALGORITHM] == "HDBSCAN":
            # Create a HDBSCAN instance with k clusters: model
            hdbscan = HDBSCAN(
                min_cluster_size=config_dict[Variables.DE_FINAL_CONFIG_PARAM])
            # Then fit the model to your data using the fit method
            model = hdbscan.fit_predict(df_to_cluster)

        # Determine the cluster labels of new_points: labels
        # group by cluster on the index of the dataframe

        tmp = original_df[config_dict[Variables.DE_FINAL_CONFIG_COLUMN]].to_frame()
        tmp = tmp.assign(Cluster=model)

        if config_dict[Variables.DE_FINAL_CONFIG_TYPE] == "Categorical":
            mode_values_df = tmp.groupby("Cluster").agg({config_dict[
                                                                Variables.DE_FINAL_CONFIG_COLUMN]: lambda x:
            x.value_counts().index[0]})
        else:
            # Determine min and max values of each cluster
            min_values_df = tmp.groupby("Cluster").agg(
                {config_dict[Variables.DE_FINAL_CONFIG_COLUMN]: "min"})
            max_values_df = tmp.groupby("Cluster").agg(
                {config_dict[Variables.DE_FINAL_CONFIG_COLUMN]: "max"})
            # Create new column 'range' with the difference between max and min values
            min_values_df = min_values_df.rename(
                columns={config_dict[Variables.DE_FINAL_CONFIG_COLUMN]: "min"})
            max_values_df = max_values_df.rename(
                columns={config_dict[Variables.DE_FINAL_CONFIG_COLUMN]: "max"})
            range_values_df = pd.concat([min_values_df, max_values_df], axis=1)
            mode_values_df = range_values_df.apply(lambda x: f"[{x['min']} - {x['max']}]", axis=1)

        tmp = tmp.groupby("Cluster").agg(
            {config_dict[Variables.DE_FINAL_CONFIG_COLUMN]: "unique"})
        tmp = tmp.rename(
            columns={config_dict[Variables.DE_FINAL_CONFIG_COLUMN]: "Values"})
        tmp["Cluster"] = mode_values_df
        return tmp

    def calculate_data_extraction_evaluation_scores(self, config_dict, df_chosen_column):
        centers = list(
                    range(config_dict['range_iteration_lower'],
                          config_dict['range_iteration_upper'],
                          config_dict['range_iteration_upper'] //
                          config_dict['number_of_scores']))

        if config_dict['chosen_type'] == "Categorical":
            # If categorical, we need to extract the tfidf vectors and use PCA to reduce the dimensionality
            tfidf_vectorizer_vectors = self._extract_tfidf_vectors(
                df_chosen_column)
            cluster_df = self._perform_pca(tfidf_vectorizer_vectors, 0.95)
        else:
            # Numerical
            cluster_df = df_chosen_column.astype(float).to_frame()

        # K-means
        if config_dict['chosen_algorithm'] == "K-means":
            scores = {}
            for center in centers:
                print(f"calculating scores for: {center}")
                scores[center] = self._get_cluster_scores_kmeans(cluster_df, center)

            # HDBSCAN
        if config_dict['chosen_algorithm'] == "HDBSCAN":
            scores = {}
            for min_sample in centers:
                print(f"calculating scores for: {min_sample}")
                scores[min_sample] = self._get_cluster_scores_hdbscan(cluster_df, min_sample)

        return {"scores":scores, "cluster_df":cluster_df.to_json()}