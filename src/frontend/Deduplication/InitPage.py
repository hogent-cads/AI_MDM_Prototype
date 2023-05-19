import streamlit as st
import extra_streamlit_components as stx

from src.frontend.Deduplication.Enums.ZinggTypesEnum import ZinggTypesEnum
from src.frontend.DatasetDisplayer.DatasetDisplayerComponent import (
    DatasetDisplayerComponent,
)
from src.frontend.enums import DialogEnum as d, VarEnum


class InitPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):
        with self.canvas.container():
            chosen_tab = stx.tab_bar(
                data=[
                    stx.TabBarItemData(id=1, title="Dataset", description=""),
                    stx.TabBarItemData(id=2, title=d.DD_DEDUPLICATION, description=""),
                ],
                default=1,
            )

            if chosen_tab == "1":
                DatasetDisplayerComponent().show()

            if chosen_tab == "2":
                self._show_deduplication_settings()

    def _show_deduplication_settings(self):
        st.subheader(d.DD_DEDUPLICATION_COLUMN_SELECTION.value)

        colA, colB, colC = st.columns([3, 3, 8])
        with colA:
            selected_col = st.selectbox(
                "Column:", st.session_state[VarEnum.SB_LOADED_DATAFRAME].columns
            )

        with colB:
            selected_type = st.selectbox("Type:", ZinggTypesEnum._member_names_)

        with colC:
            if selected_type:
                st.write("")
                st.write("")
                st.write(eval(f"ZinggTypesEnum.{selected_type}"))

        # FOR DEBUG ON RESTOS.CSV PRE-DEFINED FIELDS:
        if (VarEnum.DD_TYPE_DICT not in st.session_state) or (
            st.session_state[VarEnum.DD_TYPE_DICT] == {}
        ):
            st.session_state[VarEnum.DD_TYPE_DICT] = {
                k: "FUZZY"
                for k in st.session_state[VarEnum.SB_LOADED_DATAFRAME].columns
            }

        col_1, col_3, _ = st.columns([1, 2, 8])
        with col_1:
            add_btn = st.button(d.DD_DEDUPLICATION_CHANGE_TYPE_BTN.value)
            if add_btn:
                st.session_state[VarEnum.DD_TYPE_DICT][selected_col] = selected_type

        with col_3:
            if len(st.session_state[VarEnum.DD_TYPE_DICT].values()) > 0:
                start_training_btn = st.button(d.DD_DEDUPLICATION_START_BTN.value)
                if start_training_btn:
                    self.handler.prepare_zingg(
                        st.session_state[VarEnum.DD_TYPE_DICT],
                        st.session_state[VarEnum.SB_LOADED_DATAFRAME].to_json(),
                    )
                    st.session_state[VarEnum.GB_CURRENT_STATE] = VarEnum.ST_DD_LABELING
                    st.experimental_rerun()
        st.write("")
        st.write(d.DD_DEDUPLICATION_COLUMN_SELECTION_OVERVIEW.value)
        st.write(st.session_state[VarEnum.DD_TYPE_DICT])
