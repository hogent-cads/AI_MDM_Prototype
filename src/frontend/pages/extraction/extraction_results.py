import plotly.graph_objects as go
import streamlit as st
from kneed import KneeLocator
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

                    # Fetch scores from back-end
                    result = self.handler.calculate_data_extraction_evaluation_scores(
                        st.session_state[Variables.DE_CONFIG],
                        st.session_state[Variables.SB_LOADED_DATAFRAME][
                            st.session_state[Variables.DE_CONFIG]['chosen_column']])
                    st.session_state[Variables.DE_CLUSTER_DF] = result["cluster_df"]
                    st.session_state[Variables.DE_SCORES] = result["scores"]
                    scores = result["scores"]
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
                                                            S=3.0, curve="concave", direction="increasing",
                                                            online=False,
                                                            interp_method="interp1d", polynomial_degree=3),
                                          all_knees=True))

            with st.expander(label="Show additional information", expanded=False):

                if sum([v['inertia'] for v in scores.values()]) != 0:
                    st.write('Inertia')
                    st.write(self.plot_figure(x=centers, y=[v['inertia'] for v in scores.values()],
                                              kl=self.find_knee(x=centers, y=[v['inertia'] for v in scores.values()],
                                                                S=3.0,
                                                                curve="convex", direction="decreasing", online=True,
                                                                interp_method="interp1d", polynomial_degree=3),
                                              all_knees=False))

                st.write('CH Index')
                st.write(self.plot_figure(x=centers, y=[v['ch_index'] for v in scores.values()],
                                          kl=self.find_knee(x=centers, y=[v['ch_index'] for v in scores.values()],
                                                            S=3.0,
                                                            curve="concave", direction="decreasing", online=True,
                                                            interp_method="interp1d", polynomial_degree=3),
                                          all_knees=False))

                st.write('DB Index')
                st.write(self.plot_figure(x=centers, y=[v['db_index'] for v in scores.values()],
                                          kl=self.find_knee(x=centers, y=[v['db_index'] for v in scores.values()],
                                                            S=3.0,
                                                            curve="concave", direction="decreasing", online=True,
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
                del st.session_state['tmp']
                st.session_state[Variables.GB_CURRENT_STATE] = Variables.ST_DE_COMBINE