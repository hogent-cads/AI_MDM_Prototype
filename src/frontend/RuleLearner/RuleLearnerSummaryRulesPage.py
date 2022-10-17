from cgitb import handler
import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit.components.v1 import html
from src.frontend.Handler.IHandler import IHandler

class RuleLearnerSummaryRulesPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self): 

        with self.canvas.container():

            st.title("Gevonden Regels:")
            trgNaarDataset = st.button("<- Terug naar Dataset")
            if trgNaarDataset:
                st.session_state["currentState"] = None
                st.experimental_rerun()
            
            st.write("Filter de regels:")
            col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns([3,1,2,2,2])

            with col_t1:
                ant_set = st.multiselect(
                    'Kies de antecedentenset',
                    st.session_state["dataframe"].columns)

            with col_t2:
                st.subheader(" => ")

            with col_t3:
                con_set = st.selectbox(
                    'Kies de consequent kolom',
                    st.session_state["dataframe"].columns)

            with col_t4:
                st.download_button(
                        label="Sla geselecteerde regels op",
                        data=st.session_state["dataframe"].to_csv(index=False),
                        file_name='Rule_Learned_Dataset.csv',
                        mime='text/csv',
                    )
            
            with col_t5:
                give_suggestions = st.button("Geef beste suggesties o.b.v. selectie")
                if give_suggestions:
                    st.write("DOE CALL NAAR API, SLA RESPONS OP IN SESSION_STATE EN VERANDER VAN PAGINA")

            
            st.write(st.session_state["gevonden_rules_dataframe"])
            

            # Tabbladen met de verschillende types van gevonden regels
            # tab1, tab2, tab3 = st.tabs(["Definities", "Volledige Mappings", "Onvolledige Mappings"])
            # with tab1:
            #     st.header("Definities")

            #     if st.session_state['gevonden_rules_dict']["def"]:
            #         for idx, cr in enumerate(st.session_state['gevonden_rules_dict']["def"]):
            #             value_mapping_df = pd.DataFrame(cr.value_mapping)
            #             steedsKloppenRegelsContainer = st.expander(label = cr.rule_string, expanded=False)
            #             with steedsKloppenRegelsContainer:
                            
            #                 col1_1, _, col1_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #                 col2_1,_,  col2_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #                 with col1_1:
            #                     st.subheader("Gevonden mapping:")
                            
            #                 with col1_2:
            #                     st.subheader("Rijen waar fouten inzitten:")
            #                 with col2_1:
            #                     gb = GridOptionsBuilder.from_dataframe(value_mapping_df)
            #                     gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True, key="nietIngevuld")
            #                     gridOptions = gb.build()
            #                     grid_response = AgGrid(value_mapping_df,height= 250, gridOptions=gridOptions,fit_columns_on_grid_load = True, enable_enterprise_modules = False)
            #                     temp = grid_response['data']
            #                 with col2_2:
            #                     st.write("Geen foutieve rijen gevonden")
            #     else:
            #         st.subheader("Er werden geen definities in de dataset teruggevonden.")


            
            # with tab2:
            #     st.header("Regels die voor alle records gelden")
            #     for idx, cr in enumerate(st.session_state['gevonden_rules_dict']["always"]):
            #         value_mapping_df = pd.DataFrame(cr.value_mapping)
            #         steedsKloppenRegelsContainer = st.expander(label = cr.rule_string, expanded=False)
            #         with steedsKloppenRegelsContainer:
                        
            #             col1_1, _, col1_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #             col2_1,_,  col2_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #             with col1_1:
            #                 st.subheader("Gevonden mapping:")
                        
            #             with col1_2:
            #                 st.subheader("Rijen waar fouten inzitten:")
            #             with col2_1:
            #                 gb = GridOptionsBuilder.from_dataframe(value_mapping_df)
            #                 gb.configure_grid_options(fit_columns_on_grid_load=True)
            #                 gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True, key="nietIngevuld")
            #                 gridOptions = gb.build()
            #                 grid_response = AgGrid(value_mapping_df,height= 250, gridOptions=gridOptions,fit_columns_on_grid_load = True, enable_enterprise_modules = False)
            #                 temp = grid_response['data']
            #             with col2_2:
            #                 st.write("Geen foutieve rijen gevonden")


            # with tab3:
            #     st.header("Regels die in meer dan 95% van alle records gelden")
            #     for idx, cr in enumerate(st.session_state['gevonden_rules_dict']["not_always"]):
            #         value_mapping_df = pd.DataFrame(cr.value_mapping)
            #         # Opnieuw maken van df_to_correct op basis van ingeladen dataframe
            #         df_to_correct = st.session_state['dataframe'].iloc[cr.idx_to_correct]
            #         steedsKloppenRegelsContainer = st.expander(label = cr.rule_string, expanded=False)
            #         with steedsKloppenRegelsContainer:
                        
            #             col1_1, _, col1_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #             col2_1,_,  col2_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #             with col1_1:
            #                 st.subheader("Gevonden mapping:")
            #                 st.write(f"Geldig voor {float(cr.confidence) * 100 }% van de {len(st.session_state['dataframe'])} records")
                        
            #             with col1_2:
            #                 st.subheader("Rijen waar fouten inzitten:")
            #             with col2_1:
            #                 gb = GridOptionsBuilder.from_dataframe(value_mapping_df)
            #                 gb.configure_grid_options(fit_columns_on_grid_load=True)
            #                 gridOptions = gb.build()
            #                 grid_response = AgGrid(value_mapping_df,height= 250, gridOptions=gridOptions,fit_columns_on_grid_load = True, enable_enterprise_modules = False, key="not_always_vm" + str(idx))
            #                 temp = grid_response['data']
            #             with col2_2:
            #                 gb = GridOptionsBuilder.from_dataframe(df_to_correct)
            #                 gb.configure_grid_options(fit_columns_on_grid_load=True)
            #                 gridOptions = gb.build()
            #                 grid_response = AgGrid(df_to_correct,height= 250, gridOptions=gridOptions,fit_columns_on_grid_load = False, enable_enterprise_modules = False, key="not_always_tc" + str(idx))
            #                 temp = grid_response['data']

            st.header("Doe zelf een voorstel voor een regel en valideer deze:")

            ant_set = st.multiselect(
                'Kies de antecedentenset',
                st.session_state["dataframe"].columns
                )

            con_set = st.selectbox(
                'Kies de consequent kolom',
                st.session_state["dataframe"].columns)

            validate_own_rule = st.button("Valideer eigen regel")
            if validate_own_rule:
                st.write("VALUE MAPPING VAN CUSTOM REGEL -> POST REQUEST")
            
            st.download_button(
                label="Sla Regels op",
                data=st.session_state["dataframe"].to_csv(index=False),
                file_name='Rule_Learned_Dataset.csv',
                mime='text/csv',
            )


