import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

from src.frontend.enums.VarEnum import VarEnum


class DatasetDisplayerComponent:
    def __init__(self) -> None:
        pass

    def show(self, min_height: int = 50, max_height: int = 500, row_height: int = 60):
        st.header("Loaded dataset:")
        gb = GridOptionsBuilder.from_dataframe(
            st.session_state[VarEnum.SB_LOADED_DATAFRAME]
        )
        gb.configure_side_bar()
        gb.configure_default_column(editable=True)
        standard_grid_options = gb.build()

        extra_grid_options = {
            "alwaysShowHorizontalScroll": True,
            "alwaysShowVerticalScroll": True,
            "pagination": True,
            "paginationPageSize": len(st.session_state[VarEnum.SB_LOADED_DATAFRAME]),
        }

        grid_options = standard_grid_options | extra_grid_options
        grid_response = AgGrid(
            st.session_state[VarEnum.SB_LOADED_DATAFRAME],
            update_mode=GridUpdateMode.GRID_CHANGED,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            height=min(
                min_height
                + len(st.session_state[VarEnum.SB_LOADED_DATAFRAME]) * row_height,
                max_height,
            ),
        )
        # Check if data is changed
        if st.session_state[VarEnum.SB_LOADED_DATAFRAME] is not grid_response["data"]:
            st.session_state[VarEnum.SB_LOADED_DATAFRAME] = grid_response["data"]
            # Force cache refresh when data is changed, (However the file will not be reloaded)
            st.session_state[VarEnum.DDC_FORCE_RELOAD_CACHE] = True
