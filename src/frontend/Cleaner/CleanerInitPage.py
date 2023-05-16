import streamlit as st
import pandas as pd
from src.frontend.Handler.IHandler import IHandler
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
import re
import extra_streamlit_components as stx
import config as cfg

from src.frontend.enums.VarEnum import VarEnum
from src.frontend.enums.DialogEnum import DialogEnum as d
from src.frontend.DatasetDisplayer.DatasetDisplayerComponent import DatasetDisplayerComponent

from copy import deepcopy


class CleanerInitPage:

    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def _show_unique_values(self, series):
        # find all the unique characters in the values of the column and show the value counts
        unique_characters = set()
        series = series.astype(str)
        series.apply(lambda x: list(map(lambda y: unique_characters.add(y), x)))
        
        value_counts = {}
        series.apply(lambda x: list(map(lambda y: value_counts.update({y: value_counts.get(y, 0) + 1}) if y not in value_counts else None, x)))
        unique_characters_df = pd.DataFrame(value_counts.items(), columns=["character", "value_counts"]).sort_values(by="value_counts", ascending=False)

        # remove all the characters that are in the regex pattern [a-zA-Z0-9]
        regex_pattern_to_remove = '[a-zA-Z0-9]+'
        unique_characters_df = unique_characters_df[~unique_characters_df["character"].str.contains(regex_pattern_to_remove)]

        return unique_characters_df

    def show(self):
        chosen_tab = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Dataset", description=""),
            stx.TabBarItemData(id=2, title="Structure Detection", description=""),
            stx.TabBarItemData(id=3, title="Fuzzy Matching", description=""),
            stx.TabBarItemData(id=4, title="Cleaning Pipelines", description="")
            ], default=1)

        if chosen_tab == "1":
            DatasetDisplayerComponent().show()

        if chosen_tab == "2":
            self._show_structure_detection_tab()

        if chosen_tab == "3":
            self._show_fuzzy_matching_tab()

        if chosen_tab == "4":
            self._show_cleaning_pipelines_tab()

    def _determine_fill_na_value_based_on_type_and_column(self, type, column):

        try:
            if type == d.dc_CLEANING_FILLNA_value_MEDIAN.value:
                # calculate the median of the column
                try:
                    return pd.to_numeric(st.session_state[VarEnum.sb_LOADED_DATAFRAME][column], errors='coerce').median()
                except Exception as e:
                    return 0
            if type == d.dc_CLEANING_FILLNA_value_MEAN.value:
                # calculate the median of the column
                try:
                    return pd.to_numeric(st.session_state[VarEnum.sb_LOADED_DATAFRAME][column], errors='coerce').mean()
                except Exception as e:
                    return 0
            if type == d.dc_CLEANING_FILLNA_value_FREQ.value:
                try:
                # calculate value counts of the column and pick the value that is most frequent but not None
                    value_counts = st.session_state[VarEnum.sb_LOADED_DATAFRAME][column].value_counts()
                    value_counts = value_counts[value_counts.index != "None"]
                    return value_counts.index[0]
                except Exception as e:
                    return None
        except Exception as e:
            return None         
            
    def _show_cleaning_pipelines_tab(self):
        st.header('Cleaning Pipelines:')

        # These are reliant on the method names of the dataprep library
        cleaning_method_translations = {
            d.dc_CLEANING_method_FILLNA.value : "fillna",
            d.dc_CLEANING_method_LOWERCASE.value : "lowercase",
            d.dc_CLEANING_method_UPPERCASE.value : "uppercase",
            d.dc_CLEANING_method_REMOVE_DIGITS.value : "remove_digits",
            d.dc_CLEANING_method_REMOVE_HTML.value : "remove_html",
            d.dc_CLEANING_method_REMOVE_URL.value : "remove_urls",
            d.dc_CLEANING_method_REMOVE_PUNCTUATION.value : "remove_punctuation",
            d.dc_CLEANING_method_REMOVE_ACCENTS.value : "remove_accents",
            d.dc_CLEANING_method_REMOVE_STOPWORDS.value : "remove_stopwords",
            d.dc_CLEANING_method_REMOVE_WHITESPACE.value : "remove_whitespace",
            d.dc_CLEANING_method_REMOVE_BRACKETED.value : "remove_bracketed",
            d.dc_CLEANING_method_REMOVE_PREFIXED.value : "remove_prefixed"
        }

        cleaning_method_descriptions = {
            d.dc_CLEANING_method_FILLNA.value : d.dc_CLEANING_method_FILLNA_description.value,
            d.dc_CLEANING_method_LOWERCASE.value : d.dc_CLEANING_method_LOWERCASE_description.value,
            d.dc_CLEANING_method_UPPERCASE.value : d.dc_CLEANING_method_UPPERCASE_description.value,
            d.dc_CLEANING_method_REMOVE_DIGITS.value : d.dc_CLEANING_method_REMOVE_DIGITS_description.value,
            d.dc_CLEANING_method_REMOVE_HTML.value : d.dc_CLEANING_method_REMOVE_HTML_description.value,
            d.dc_CLEANING_method_REMOVE_URL.value : d.dc_CLEANING_method_REMOVE_URL_description.value,
            d.dc_CLEANING_method_REMOVE_PUNCTUATION.value : d.dc_CLEANING_method_REMOVE_PUNCTUATION_description.value,
            d.dc_CLEANING_method_REMOVE_ACCENTS.value : d.dc_CLEANING_method_REMOVE_ACCENTS_description.value,
            d.dc_CLEANING_method_REMOVE_STOPWORDS.value : d.dc_CLEANING_method_REMOVE_STOPWORDS_description.value,
            d.dc_CLEANING_method_REMOVE_WHITESPACE.value : d.dc_CLEANING_method_REMOVE_WHITESPACE_description.value,
            d.dc_CLEANING_method_REMOVE_BRACKETED.value : d.dc_CLEANING_method_REMOVE_BRACKETED_description.value,
            d.dc_CLEANING_method_REMOVE_PREFIXED.value : d.dc_CLEANING_method_REMOVE_PREFIXED_description.value
        }

        colG_1, colG_2, colG_3 = st.columns([1, 1, 1])

        st.write("")
        st.write("")
        colI_1, colI_3, colI4,  _ = st.columns([4, 3, 3,3])

        with colI_1:
            chosen_column = st.selectbox(
                d.dc_CLEANING_SELECT_COLUMN.value,
                st.session_state[VarEnum.sb_LOADED_DATAFRAME].columns)

        with colI_3:
            st.write("")
            st.write("")
            if st.button(d.dc_CLEANING_APPLY_PIPELINE_COLUMN.value):

                # Make a copy of the pipeline, this is the one that will be given to the backend.
                # The pipeline in the session state will be used to show the pipeline in the frontend
                copied_pipeline = deepcopy(st.session_state[VarEnum.dc_PIPELINE])

                # iterate over alle value parameters in the pipeline
                for item in copied_pipeline["text"]:
                    for k,v in item.items():
                        if k == "parameters":
                            if "value" in v:
                                value = v["value"]
                                if value in [d.dc_CLEANING_FILLNA_value_MEAN.value, d.dc_CLEANING_FILLNA_value_MEDIAN.value, d.dc_CLEANING_FILLNA_value_MODE.value]:
                                        value = self._determine_fill_na_value_based_on_type_and_column(value, chosen_column)
                                
                                # replace "MEAN", "MODE" or "MEDIAN" with the actual value
                                st.write(value)
                                item[k]["value"] = value

                st.session_state[VarEnum.dc_CLEANED_COLUMN] = pd.DataFrame(self.handler.clean_dataframe_dataprep(
                            dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME][chosen_column].to_frame().to_json(), 
                            custom_pipeline=copied_pipeline))
                st.session_state[VarEnum.dc_CLEANED_COLUMN].index = st.session_state[VarEnum.dc_CLEANED_COLUMN].index.astype(int)
                st.session_state[VarEnum.sb_LOADED_DATAFRAME][chosen_column] = st.session_state[VarEnum.dc_CLEANED_COLUMN][chosen_column]
                st.write("Column successfully cleaned.")

                

        with colG_2:
            cleaning_methods_list = [d.dc_CLEANING_method_LOWERCASE.value,
                                     d.dc_CLEANING_method_UPPERCASE.value,
                                     d.dc_CLEANING_method_FILLNA.value,
                                     d.dc_CLEANING_method_REMOVE_DIGITS.value,
                                     d.dc_CLEANING_method_REMOVE_HTML.value,
                                     d.dc_CLEANING_method_REMOVE_URL.value,
                                     d.dc_CLEANING_method_REMOVE_PUNCTUATION.value,
                                     d.dc_CLEANING_method_REMOVE_ACCENTS.value,
                                     d.dc_CLEANING_method_REMOVE_STOPWORDS.value,
                                     d.dc_CLEANING_method_REMOVE_WHITESPACE.value,
                                     d.dc_CLEANING_method_REMOVE_BRACKETED.value,
                                     d.dc_CLEANING_method_REMOVE_PREFIXED.value]
            
            special_methods = [ d.dc_CLEANING_method_FILLNA.value,
                                d.dc_CLEANING_method_REMOVE_STOPWORDS.value,
                                d.dc_CLEANING_method_REMOVE_BRACKETED.value,
                                d.dc_CLEANING_method_REMOVE_PREFIXED.value]

            cleaning_method = st.selectbox(
                d.dc_CLEANING_method_selection.value, cleaning_methods_list)
            
            colH_1, colH_2 = st.columns([1, 1])
            with colH_1:
                st.write(cleaning_method_descriptions[cleaning_method])
            with colH_2:
                if cleaning_method in special_methods:
                    if cleaning_method == d.dc_CLEANING_method_REMOVE_BRACKETED.value:
                        value = str(set(st.multiselect(d.dc_CLEANING_SELECT_BRACKET, ['()', '[]', '{}', '<>'])))
                    else:
                        value = st.text_input("Optional parameter", "")
            
        with colI4:
            st.write("")
            st.write("")
            if st.button(d.dc_CLEANING_APPLY_PIPELINE_ALL.value):
            
                # calculate value if needed
                if cleaning_method == d.dc_CLEANING_method_FILLNA.value:
                    # check if there is a special value in value:
                    if value in [d.dc_CLEANING_FILLNA_value_MEAN.value, d.dc_CLEANING_FILLNA_value_MEDIAN.value, d.dc_CLEANING_FILLNA_value_MODE.value]:
                        value = self._determine_fill_na_value_based_on_type_and_column(value, chosen_column)
                else:

                    # HIER VERDER DOEN
                    value = None

                for e in st.session_state[VarEnum.sb_LOADED_DATAFRAME].columns:
                    if value in [d.dc_CLEANING_FILLNA_value_MEAN.value, d.dc_CLEANING_FILLNA_value_MEDIAN.value, d.dc_CLEANING_FILLNA_value_MODE.value]:
                        correct_value = self._determine_fill_na_value_based_on_type_and_column(value, e)
                        st.write(correct_value)
                    # change value of parameter to correct value

                    self._apply_pipeline(e)
                st.write(d.dc_CLEANING_CHANGES_APPLIED.value)
        

        with colG_3:
            st.write("")
            st.write("")
            if st.button(d.dc_CLEANING_ADD_PIPELINE.value):
                # check if the pipeline is empty
                if st.session_state[VarEnum.dc_PIPELINE] == {}:
                    st.session_state[VarEnum.dc_PIPELINE]['text'] = []

                to_append = {}
                if cleaning_method not in special_methods:
                    to_append = {'operator': cleaning_method_translations[cleaning_method]}
                if cleaning_method == d.dc_CLEANING_method_FILLNA.value:
                    to_append = {'operator': cleaning_method_translations[cleaning_method], 'parameters' : {'value': str(value)}} 
                if cleaning_method == d.dc_CLEANING_method_REMOVE_BRACKETED.value:
                    to_append = {'operator': cleaning_method_translations[cleaning_method], 'parameters' : {'brackets': value}}
                if cleaning_method == d.dc_CLEANING_method_REMOVE_PREFIXED.value:
                    to_append = {'operator': cleaning_method_translations[cleaning_method], 'parameters' : {'prefix': value}}
                st.session_state[VarEnum.dc_PIPELINE]['text'].append(to_append)
                    

            
            if st.button(d.dc_CLEANING_CLEAR_PIPELINE.value):
                st.session_state[VarEnum.dc_PIPELINE] = {}

        with colG_1:
            st.subheader(d.dc_CLEANING_CURRENT_PIPELINE.value)
            st.write(st.session_state[VarEnum.dc_PIPELINE])

    def _apply_pipeline(self, col):       
        st.session_state[VarEnum.dc_CLEANED_COLUMN] = pd.DataFrame(self.handler.clean_dataframe_dataprep(
                            dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME][col].to_frame().to_json(), 
                            custom_pipeline=st.session_state[VarEnum.dc_PIPELINE]))
        st.session_state[VarEnum.dc_CLEANED_COLUMN].index = st.session_state[VarEnum.dc_CLEANED_COLUMN].index.astype(int)
        st.session_state[VarEnum.sb_LOADED_DATAFRAME][col] = st.session_state[VarEnum.dc_CLEANED_COLUMN][col]

    def _show_structure_detection_tab(self):
        st.header('Structure Detection:')
        colA_1, colA_2, colA_3 = st.columns([1, 1, 1])
        with colA_1:
            chosen_column = st.selectbox(
                "Select a column to detect the structure of the values",
                st.session_state[VarEnum.sb_LOADED_DATAFRAME].columns)
        with colA_2:
            extra_exceptions = "".join(st.multiselect(
                "Select the characters that you want to keep in the pattern",
                self._show_unique_values(
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME][chosen_column])["character"].tolist()))
        with colA_3:
            st.write("")
            st.write("")
            compress = st.checkbox("Compress the found patterns")

        simple_repr = pd.Series(
            self.handler.structure_detection(
                st.session_state[VarEnum.sb_LOADED_DATAFRAME][chosen_column].to_json(),
                extra_exceptions, compress))
    

        series_for_aggrid = (simple_repr.value_counts(normalize=True)
                                        .copy(deep=True))
        series_for_aggrid = (series_for_aggrid.rename_axis('pattern')
                                              .reset_index(name='percentage'))
        colB_1, _, colB_3 = st.columns([8, 1, 14])
        with colB_1:
            st.write("The found patterns are:")
            gb = GridOptionsBuilder.from_dataframe(series_for_aggrid)
            gb.configure_side_bar()
            gb.configure_default_column(
                groupable=True, value=True,
                enableRowGroup=True, aggFunc="sum", editable=False)
            gb.configure_selection(
                'single', pre_selected_rows=[], use_checkbox=True,
                groupSelectsChildren=True, groupSelectsFiltered=True)
            extra_grid_options_1 = {
            "alwaysShowHorizontalScroll": True,
            "alwaysShowVerticalScroll": True,
                    }
            response_patterns = AgGrid(
                series_for_aggrid,
                editable=False,
                gridOptions=gb.build() | extra_grid_options_1,
                data_return_mode="filtered_and_sorted",
                update_mode="model_changed",
                fit_columns_on_grid_load=True,
                theme="streamlit",
                enable_enterprise_modules=False,
            )
            st.session_state["idx_of_structure_df"] = None

        with colB_3:
            if response_patterns["selected_rows"]:
                # show the records that match the selected pattern
                selected_pattern = (response_patterns["selected_rows"][0]["pattern"]
                                    if len(response_patterns["selected_rows"]) > 0
                                    else None)
                
                if selected_pattern is not None:
                    st.write("The records that match the selected pattern are:")
                    df_for_aggrid2 = st.session_state[VarEnum.sb_LOADED_DATAFRAME][simple_repr.values == selected_pattern]
                    
                    if st.session_state["idx_of_structure_df"] is None:
                        st.session_state["idx_of_structure_df"] = list(df_for_aggrid2.index)
                    gb2 = GridOptionsBuilder.from_dataframe(df_for_aggrid2)
                    gb2.configure_side_bar()
                    gb2.configure_default_column(
                        groupable=False, value=True,
                        enableRowGroup=True, aggFunc="sum", editable=True)
                    gridOptions = gb2.build()
                    extra_grid_options_2 = {
                        "alwaysShowHorizontalScroll": True,
                        "alwaysShowVerticalScroll": True,
                        "pagination": True,
                        "paginationPageSize": len(st.session_state[VarEnum.sb_LOADED_DATAFRAME]),
                    }
                    grid = AgGrid(df_for_aggrid2, gridOptions=gridOptions | extra_grid_options_2,
                                  enable_enterprise_modules=False, height=500)
                    
                    grid['data'].index = st.session_state["idx_of_structure_df"]

                    if st.button("Save Changes"):
                        # Replace values in the dataframe with the (possibly) new values
                        st.session_state[VarEnum.sb_LOADED_DATAFRAME].loc[grid['data'].index] = grid['data']
                        st.experimental_rerun()
            else:
                st.session_state["idx_of_structure_df"] = None

    def _show_fuzzy_matching_tab(self):
        st.header('Fuzzy Matching:')
        colC_1, colC_2, colC_3 = st.columns([1, 1, 1])
        with colC_1:
            chosen_column = st.selectbox(
                "Select the column that you want to cluster:",
                st.session_state[VarEnum.sb_LOADED_DATAFRAME].columns)
        with colC_2:
            cluster_method = st.selectbox(
                "Select the cluster method",
                ["fingerprint", "phonetic-fingerprint",
                    "ngram-fingerprint", "levenshtein"])

            
        fuzzy_matching_form = st.form(key='fuzzy_matching_form')
        with fuzzy_matching_form:
            
            colD_2, colD_1, _  = st.columns([1, 3, 2])

            with colD_1:
                n_gram = 0
                radius = 0
                block_size = 0
                if cluster_method == 'ngram-fingerprint':
                    colE_1, _ = st.columns([1, 1])
                    with colE_1:
                        n_gram = st.slider(
                            'The Number of N-Grams',
                            min_value=2, max_value=10, value=2)
                if cluster_method == 'levenshtein':
                    colF_1, colF_2 = st.columns([1, 1])
                    with colF_1:
                        radius = st.slider(
                            'The Radius',
                            min_value=1, max_value=10, value=2)
                    with colF_2:
                        block_size = st.slider(
                            'The Block Size',
                            min_value=1, max_value=10, value=6)
                        
            with colD_2:
                st.write("")
                fuzzy_matching_btn = st.form_submit_button(label='Cluster')

        if fuzzy_matching_btn:
            # Iterate over clusters
            st.session_state['list_of_cluster_view'] = []
            list_of_fuzzy_clusters = []
            # delete all keys that start with 'fuzzy_merge'
            for key in list(st.session_state.keys()):
                if key.startswith('fuzzy_merge'):
                    del st.session_state[key]
                    

            for cluster_id, list_of_values in self.handler.fuzzy_match_dataprep(
                    dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME][chosen_column].to_frame().to_json(),
                    df_name=st.session_state[VarEnum.sb_LOADED_DATAFRAME_NAME],
                    col=chosen_column,
                    cluster_method=cluster_method,
                    ngram=n_gram,
                    radius=radius,
                    block_size=block_size).items():
                if f'fuzzy_merge_{cluster_id}' not in st.session_state:
                    st.session_state[f'fuzzy_merge_{cluster_id}'] = True
                # Create a view for each cluster
                list_of_fuzzy_clusters.append(FuzzyClusterView(
                    cluster_id, list_of_values,
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME][chosen_column]))
            st.session_state["list_of_fuzzy_cluster_view"] = list_of_fuzzy_clusters

        if st.session_state["list_of_fuzzy_cluster_view"] != []:
            st.header("Found clusters:")

            col0, _ = st.columns([6,2])
            with col0:
                sort_clusters = st.selectbox(
                'Sort clusters on:',
                ('Cluster size: increasing', 'Cluster size: decreasing'))
                if sort_clusters == 'Cluster size: increasing':
                    st.session_state["list_of_fuzzy_cluster_view"] = sorted(st.session_state["list_of_fuzzy_cluster_view"], key=lambda x: len(x.distinct_values_in_cluster), reverse=False)
                if sort_clusters == 'Cluster size: decreasing':
                    st.session_state["list_of_fuzzy_cluster_view"] = sorted(st.session_state["list_of_fuzzy_cluster_view"], key=lambda x: len(x.distinct_values_in_cluster), reverse=True)

            st.write("")
            st.write("")
            sub_rows_to_use = self. _create_pagination(
                "page_number_fuzzy",
                st.session_state["list_of_fuzzy_cluster_view"], 5)
            for idx, cv in enumerate(sub_rows_to_use):
                self._create_cluster_card(idx, cv)
            if st.button("Bevestig clusters"):
                self._merge_clusters(st.session_state["list_of_fuzzy_cluster_view"],chosen_column)
                st.session_state[VarEnum.gb_CURRENT_STATE] = None
                st.session_state["list_of_fuzzy_cluster_view"] = []
                st.experimental_rerun()
        else:
            st.markdown("**No clusters have been found**")

        self._clear_js_containers()
        self._give_custom_css_to_container()

    def _create_pagination(self, key, cols_to_use, N):
        # A variable to keep track of which product we are currently displaying
        if key not in st.session_state:
            st.session_state[key] = 0

        last_page = len(cols_to_use) // N

        # Add a next button and a previous button
        prev, _, tussen, _, next, _ = st.columns([3, 1, 2, 1, 3, 2])

        if next.button("Next results"):
            if st.session_state[key] + 1 > last_page:
                st.session_state[key] = 0
            else:
                st.session_state[key] += 1

        if prev.button("Previous results"):
            if st.session_state[key] - 1 < 0:
                st.session_state[key] = last_page
            else:
                st.session_state[key] -= 1

        with tussen:
            st.write(str(st.session_state[key] + 1) + "/" +
                     str(last_page + 1) + " (" + str(len(cols_to_use)) +
                     " resultaten)")

        # Get start and end indices of the next page of the dataframe
        start_idx = st.session_state[key] * N
        end_idx = (1 + st.session_state[key]) * N

        # Index into the sub dataframe
        return cols_to_use[start_idx:end_idx]

    def _merge_clusters(self, list_of_cluster_view, column_name):
        # Itereer over alle clusterview
        for cv in list_of_cluster_view:
            if st.session_state[f'fuzzy_merge_{cv.cluster_id}']:
                for val_to_replace in cv.selected_values:
                    # Look for value e in the dataframe in column column_name
                    # and replace it with the value in the cluster
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME][column_name] = st.session_state[VarEnum.sb_LOADED_DATAFRAME][column_name].astype(str).replace(
                        str(val_to_replace), str(cv.new_cell_value))
        

    def _create_cluster_card(self, idx, cv, min_height:int = 100, max_height:int = 250, row_height:int = 30):

        cont = st.container()
        
        with cont:
            col0, colA, colB, colC, _ = st.columns([2,4,2,2,4])
            with col0:
                st.subheader(f'Cluster #{cv.cluster_id}')
            with colA:
                gb1 = GridOptionsBuilder.from_dataframe(cv.distinct_values_in_cluster)
                gb1.configure_side_bar()
                gb1.configure_default_column(editable=False)
                gb1.configure_selection(header_checkbox=True, pre_select_all_rows=True, selection_mode="multiple", use_checkbox=True)
                gridOptions = gb1.build()
                extra_grid_options = {
                        "alwaysShowHorizontalScroll": True,
                        "alwaysShowVerticalScroll": True,
                        "pagination": True,
                        "paginationPageSize": len(cv.distinct_values_in_cluster),
                    } 
                gridOptionsFull = gridOptions | extra_grid_options
                tmp = AgGrid(cv.distinct_values_in_cluster, gridOptions=gridOptionsFull, enable_enterprise_modules=False, update_mode="SELECTION_CHANGED", height=min(min_height + len(cv.distinct_values_in_cluster) * row_height, max_height))
                cv.selected_rows = tmp['selected_rows']
            with colB:
                # checkbox om te mergen, default actief
                    st.session_state[f'fuzzy_merge_{cv.cluster_id}'] = st.checkbox('Voeg samen',value=True, key=f'key_fuzzy_merge_{cv.cluster_id}')

            with colC:
                # st.write("Verander naar")
                st.session_state[f'new_value_{cv.cluster_id}'] = st.text_input('New value', value=cv.new_cell_value, key=f'key_new_value_{cv.cluster_id}')
                cv.set_new_cell_value(st.session_state[f'new_value_{cv.cluster_id}'])

            customSpan = rf"""
                <span id="duplicateCardsFinder{cv.cluster_id}">
                </span>
                """
            st.markdown(customSpan,unsafe_allow_html=True)
            js = f'''<script>
            containerElement = window.parent.document.getElementById("duplicateCardsFinder{cv.cluster_id}").parentElement.parentElement.parentElement.parentElement.parentElement
            containerElement.setAttribute('class', 'materialcard')
            </script>
            '''
            st.components.v1.html(js)

    def _clear_js_containers(self):
        js = f'''<script>
            iframes = window.parent.document.getElementsByTagName("iframe")
            for (var i=0, max=iframes.length; i < max; i++)
                iframes[i].title == "st.iframe" ? iframes[i].style.display = "none" : iframes[i].style.display = "block";
            </script>
            '''
        st.components.v1.html(js)
        

    def _give_custom_css_to_container(self):
        customSpan = rf"""
        <span id="containerDuplicateCardsFinder">
        </span>
        """
        st.markdown(customSpan,unsafe_allow_html=True)
        js = '''<script>
        containerElement = window.parent.document.getElementById("containerDuplicateCardsFinder").parentElement.parentElement.parentElement.parentElement.parentElement
        containerElement.setAttribute('id', 'containerDuplicateCardsFuzzy')
        </script>
        '''
        st.components.v1.html(js)

class FuzzyClusterView:

    def __init__(self, cluster_id, list_of_values, column_as_series) -> None:
        cfg.logger.debug(f"FuzzyClusterView: __init__: cluster_id = {cluster_id}," +
                         f"list_of_values = {list_of_values}, " +
                         f"column_as_series = {column_as_series}")
        self.cluster_id = cluster_id
        column_as_series = column_as_series.astype(str)
        # check how many values in column_as_series are in list_of_values
        # transform list_of_values to dataframe with index as separate column
        self.distinct_values_in_cluster = column_as_series[
            column_as_series.isin(list_of_values)].value_counts().\
            reset_index(name='count').rename(columns={'index': 'values'})
        self.merge = False
        # take max value of distinct_values_in_cluster
        self.new_cell_value = self.distinct_values_in_cluster.values[0][0]
        self.selected_values = list(self.distinct_values_in_cluster['values'])

    def set_new_cell_value(self, new_cell_value):
        self.new_cell_value = new_cell_value