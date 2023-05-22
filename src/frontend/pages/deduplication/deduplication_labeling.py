import streamlit as st
import pandas as pd


from st_aggrid import GridOptionsBuilder, AgGrid

from src.frontend.enums import Dialog as d, Variables


class ZinggLabelPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):
        st.header(d.DD_DEDUPLICATION.value)
        stats = st.container()
        if Variables.DD_CURRENT_LABEL_ROUND not in st.session_state:
            st.session_state[Variables.DD_CURRENT_LABEL_ROUND] = pd.DataFrame(
                self.handler.zingg_unmarked_pairs()
            )
        if Variables.DD_LABEL_STATS not in st.session_state:
            st.session_state[Variables.DD_LABEL_STATS] = self.handler.zingg_get_stats()

        reponse_error_container = st.empty()

        st.subheader(d.DD_DEDUPLICATION_PAIRS_TO_MARK.value)
        # group by z_cluster and create a new zingg_label_card for each cluster
        container_for_cards = st.container()
        with container_for_cards:
            self._give_custom_css_to_container()
            counter = 0
            for z_cluster_id, z_cluster_df in st.session_state[
                Variables.DD_CURRENT_LABEL_ROUND
            ].groupby("z_cluster"):
                counter += 1
                self._create_zingg_label_card(z_cluster_df, z_cluster_id, counter)
                st.write("")
                st.write("")

        with stats:
            colB_1, colB_2 = st.columns([1, 1])
            with colB_1:
                sum_stats = sum(st.session_state[Variables.DD_LABEL_STATS].values())
                st.write(
                    f"Previous Round(s): {st.session_state[Variables.DD_LABEL_STATS]['match_files']}/{sum_stats} MATCHES, {st.session_state[Variables.DD_LABEL_STATS]['no_match_files']}/{sum_stats} NON-MATCHES, {st.session_state[Variables.DD_LABEL_STATS]['unsure_files']}/{sum_stats} UNSURE"
                )
                # st.write("Previous Round(s): " + self.handler.zingg_get_stats())
                st.write(
                    "Current labeling round: {}/{} MATCHES, {}/{} NON-MATCHES, {}/{} UNSURE".format(
                        len(
                            st.session_state[Variables.DD_CURRENT_LABEL_ROUND][
                                st.session_state[
                                    Variables.DD_CURRENT_LABEL_ROUND
                                ].z_isMatch
                                == 1
                            ]
                        )
                        // 2,
                        len(st.session_state[Variables.DD_CURRENT_LABEL_ROUND]) // 2,
                        len(
                            st.session_state[Variables.DD_CURRENT_LABEL_ROUND][
                                st.session_state[
                                    Variables.DD_CURRENT_LABEL_ROUND
                                ].z_isMatch
                                == 0
                            ]
                        )
                        // 2,
                        len(st.session_state[Variables.DD_CURRENT_LABEL_ROUND]) // 2,
                        len(
                            st.session_state[Variables.DD_CURRENT_LABEL_ROUND][
                                st.session_state[
                                    Variables.DD_CURRENT_LABEL_ROUND
                                ].z_isMatch
                                == 2
                            ]
                        )
                        // 2,
                        len(st.session_state[Variables.DD_CURRENT_LABEL_ROUND]) // 2,
                    )
                )
            with colB_2:
                colB_2_1, colB_2_2, colB_2_3 = st.columns([1, 1, 1])
                with colB_2_1:
                    st.write("")
                    next = st.button(d.DD_DEDUPLICATION_UPDATE_BTN.value)
                with colB_2_2:
                    st.write("")
                    clear = st.button(d.DD_DEDUPLICATION_CLEAR_BTN.value)
                with colB_2_3:
                    st.write("")
                    finish = st.button(d.DD_DEDUPLICATION_FINISH_BTN.value)

        if next:
            _ = self.handler.zingg_mark_pairs(
                st.session_state[Variables.DD_CURRENT_LABEL_ROUND].to_json()
            )
            _ = self.handler.run_zingg_phase("findTrainingData")
            st.session_state[Variables.DD_CURRENT_LABEL_ROUND] = pd.DataFrame(
                self.handler.zingg_unmarked_pairs()
            )
            st.session_state[Variables.DD_LABEL_STATS] = self.handler.zingg_get_stats()
            st.experimental_rerun()

        if clear:
            _ = self.handler.zingg_clear()
            _ = self.handler.run_zingg_phase("findTrainingData")
            st.session_state[Variables.DD_CURRENT_LABEL_ROUND] = pd.DataFrame(
                self.handler.zingg_unmarked_pairs()
            )
            st.session_state[Variables.DD_LABEL_STATS] = self.handler.zingg_get_stats()
            st.experimental_rerun()

        if finish:
            # Moet nog een nagegaan worden of model gemaakt is, of er een error is opgetreden door te weinig gelaabelde data => check op bestaan van folder 'model'
            response = self.handler.run_zingg_phase("train").json()
            if response == "200":
                st.session_state[
                    Variables.GB_CURRENT_STATE
                ] = Variables.ST_DD_REDIRECT_CLUSTERING
                st.experimental_rerun()
            else:
                with reponse_error_container:
                    st.error(d.DD_DEDUPLICATION_MODEL_FAIL_MESSAGE.value)

        self._clear_js_containers()

    def _create_zingg_label_card(
        self,
        grouped_df,
        z_cluster_id,
        idx,
        min_height=50,
        max_height=500,
        row_height=50,
    ):
        fields = st.session_state[Variables.DD_TYPE_DICT].keys()

        cont_card = st.container()
        with cont_card:
            colLeft, colRight = st.columns([3, 1])
            with colLeft:
                st.write("#" + str(idx))
                gb1 = GridOptionsBuilder.from_dataframe(
                    grouped_df[[c for c in grouped_df.columns if c in fields]]
                )
                gb1.configure_default_column(editable=False)
                gridOptions = gb1.build()
                extra_grid_options = {
                    "alwaysShowHorizontalScroll": True,
                    "pagination": True,
                    "paginationPageSize": len(grouped_df),
                }
                _ = AgGrid(
                    grouped_df[[c for c in grouped_df.columns if c in fields]],
                    gridOptions=gridOptions | extra_grid_options,
                    height=min(
                        min_height
                        + len(
                            grouped_df[[c for c in grouped_df.columns if c in fields]]
                        )
                        * row_height,
                        max_height,
                    ),
                    key="grid_" + z_cluster_id,
                )

            with colRight:
                if grouped_df["z_prediction"].mean() > 0:
                    colAA, colBB = st.columns([1, 1])
                    with colAA:
                        st.write(
                            d.DD_DEDUPLICATION_PREDICTION_SCORE,
                            str(format(grouped_df["z_score"].mean() * 100, ".2f"))
                            + "%",
                        )
                    with colBB:
                        st.write(
                            f"{d.DD_DEDUPLICATION_PREDICTION} {d.DD_DEDUPLICATION_LABEL_IS_A_MATCH.value if (grouped_df['z_prediction'].mean() > 0) else d.DD_DEDUPLICATION_LABEL_IS_NOT_A_MATCH.value}"
                        )
                else:
                    st.write("")
                    st.write("")
                    st.write("")

                choice = st.selectbox(
                    d.DD_DEDUPLICATION_LABEL_SELECTBOX.value,
                    [
                        d.DD_DEDUPLICATION_LABEL_IS_A_MATCH.value,
                        d.DD_DEDUPLICATION_LABEL_IS_NOT_A_MATCH.value,
                        d.DD_DEDUPLICATION_LABEL_UNSURE.value,
                    ],
                    index=2,
                    key="selectbox_" + z_cluster_id,
                )
                if choice == d.DD_DEDUPLICATION_LABEL_IS_A_MATCH.value:
                    st.session_state[Variables.DD_CURRENT_LABEL_ROUND].loc[
                        st.session_state[Variables.DD_CURRENT_LABEL_ROUND]["z_cluster"]
                        == z_cluster_id,
                        "z_isMatch",
                    ] = 1
                if choice == d.DD_DEDUPLICATION_LABEL_IS_NOT_A_MATCH.value:
                    st.session_state[Variables.DD_CURRENT_LABEL_ROUND].loc[
                        st.session_state[Variables.DD_CURRENT_LABEL_ROUND]["z_cluster"]
                        == z_cluster_id,
                        "z_isMatch",
                    ] = 0
                if choice == d.DD_DEDUPLICATION_LABEL_UNSURE.value:
                    st.session_state[Variables.DD_CURRENT_LABEL_ROUND].loc[
                        st.session_state[Variables.DD_CURRENT_LABEL_ROUND]["z_cluster"]
                        == z_cluster_id,
                        "z_isMatch",
                    ] = 2

            customSpan = rf"""
                <span id="duplicateCardsFinder{z_cluster_id}">
                </span>
                """
            st.markdown(customSpan, unsafe_allow_html=True)
            js = f"""<script>
            containerElement = window.parent.document.getElementById("duplicateCardsFinder{z_cluster_id}").parentElement.parentElement.parentElement.parentElement.parentElement
            containerElement.setAttribute('class', 'materialcard')
            </script>
            """
            st.components.v1.html(js)

    def _clear_js_containers(self):
        js = """<script>
            iframes = window.parent.document.getElementsByTagName("iframe")
            for (var i=0, max=iframes.length; i < max; i++)
                iframes[i].title == "st.iframe" ? iframes[i].style.display = "none" : iframes[i].style.display = "block";
            </script>
            """
        st.components.v1.html(js)

    def _give_custom_css_to_container(self):
        customSpan = r"""
        <span id="containerDuplicateCardsFinder">
        </span>
        """
        st.markdown(customSpan, unsafe_allow_html=True)
        js = """<script>
        containerElement = window.parent.document.getElementById("containerDuplicateCardsFinder").parentElement.parentElement.parentElement.parentElement.parentElement
        containerElement.setAttribute('id', 'containerDuplicateCards')
        </script>
        """
        st.components.v1.html(js)
