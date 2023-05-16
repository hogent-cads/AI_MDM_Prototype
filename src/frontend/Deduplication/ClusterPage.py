import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid
import hashlib

from src.frontend.enums.VarEnum import VarEnum
from src.frontend.enums.DialogEnum import DialogEnum as d

class ZinggClusterRedirectPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def redirect_get_clusters(self):
        st.session_state[VarEnum.dd_CLUSTER_DF] = pd.DataFrame(self.handler.zingg_get_clusters())
        # value_counts of values in cluster_id kolom and keep the cluster°id where there are more than 2 records
        # cluster_ids = st.session_state['zingg_clusters_df']['z_cluster'].value_counts()[st.session_state['zingg_clusters_df']['z_cluster'].value_counts() >= 2].index.tolist()

        cluster_ids = st.session_state[VarEnum.dd_CLUSTER_DF]['z_cluster'].value_counts()[st.session_state[VarEnum.dd_CLUSTER_DF]['z_cluster'].value_counts() >= 0].index.tolist()
        # for each cluster_id, get the records and create a ClusterView
        list_of_cluster_view = []
        for cluster_id in cluster_ids:
            records_df = st.session_state[VarEnum.dd_CLUSTER_DF][st.session_state[VarEnum.dd_CLUSTER_DF]['z_cluster'] == cluster_id]

            if len(records_df)> 1:
                cluster_low = records_df['z_minScore'].min()
                cluster_high = records_df['z_maxScore'].max()
                # cluster confidence is the average of the z_lower and z_higher values in the column
                cluster_confidence  = (records_df['z_minScore'].mean() + records_df['z_maxScore'].mean()) / 2
                # new_row is the row that with the highest 'cluster_high' value
                new_row = records_df[records_df['z_minScore'] == records_df['z_minScore'].max()][:1]
                list_of_cluster_view.append(ZinggClusterView(cluster_id, cluster_confidence, records_df.drop(['z_minScore', 'z_maxScore', 'z_cluster'], axis=1), new_row, cluster_low, cluster_high))
            else:
                list_of_cluster_view.append(ZinggClusterView(cluster_id, 0, records_df.drop(['z_minScore', 'z_maxScore', 'z_cluster'], axis=1), records_df.drop(['z_minScore', 'z_maxScore', 'z_cluster'], axis=1), 0, 0))

        st.session_state['list_of_cluster_view'] = list_of_cluster_view

        st.session_state[VarEnum.gb_CURRENT_STATE] = VarEnum.st_DD_Clustering
        st.experimental_rerun()

class ZinggClusterPage:

    TEXT_DEDUP_FALSE = "kept, but non-primary key values will be changed to:"
    TEXT_DEDUP_TRUE = "deleted and replaced with one record:"
    
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler
        
    def _createPaginering(self, key, colstoUse, N):
        # filter colstoUse based on length of the records in records_df
        colstoUse = [x for x in colstoUse if len(x.records_df) > 1]
        # A variable to keep track of which product we are currently displaying
        if key not in st.session_state:
            st.session_state[key] = 0
        
        last_page = len(colstoUse) // N

        # Add a next button and a previous button
        prev, _, tussen, _ ,next = st.columns([2,1,2,1,2])

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
            st.write( str(st.session_state[key] +1) + "/"+ str(last_page +1) +" (" + str(len(colstoUse)) +" resultaten)")

        # Get start and end indices of the next page of the dataframe
        start_idx = st.session_state[key] * N 
        end_idx = (1 + st.session_state[key]) * N 

        # Index into the sub dataframe
        return colstoUse[start_idx:end_idx]

    def show(self): 
        with self.canvas.container(): 
            st.title("Found Clusters")
            # Give which columns are primary keys
            pks = st.multiselect("Select the columns that form primary key, they well be left alone during merging of records", st.session_state[VarEnum.sb_LOADED_DATAFRAME].columns)

            col0, col1 = st.columns([6,2])
            with col0:
                sort_clusters = st.selectbox(
                'Sort clusters on:',
                ('Amount of records in a cluster', 'Cluster confidence score', 'Lowest cluster Similairty', 'Highest cluster Similairty'))
                if sort_clusters == 'Cluster confidence score':
                    st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: x.cluster_confidence, reverse=True)
                if sort_clusters == 'Amount of records in a cluster':
                    st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: len(x.records_df), reverse=True)
                if sort_clusters == 'Lowest cluster Similairty':
                    st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: x.cluster_low, reverse=False)
                if sort_clusters == 'Highest cluster Similairty':
                    st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: x.cluster_high, reverse=True)

            for cv in st.session_state["list_of_cluster_view"]:
                if f'merge_{cv.cluster_id}' not in st.session_state:
                    st.session_state[f'merge_{cv.cluster_id}'] = True
                if f'dedup_{cv.cluster_id}' not in st.session_state:
                    st.session_state[f'dedup_{cv.cluster_id}'] = self.TEXT_DEDUP_FALSE

            with col1:
                st.write("")
                st.write("")
                confirm_cluster = st.button("Confirm clusters")

            # Als test toon de eerste 5 elementen
            sub_rowstoUse = self. _createPaginering("page_number_Dedupe", st.session_state["list_of_cluster_view"], 5)

            # give css to div where all cluster cards are located
            container_for_cards = st.container()
            with container_for_cards:
                self._give_custom_css_to_container()
                for idx, cv in enumerate(sub_rowstoUse):
                    self._create_cluster_card(idx, cv, pks=pks)

            if confirm_cluster:
                self._merge_clusters(st.session_state["list_of_cluster_view"], pks)
                st.experimental_rerun()
            self._clear_js_containers()
                
    def _merge_clusters(self, list_of_cluster_view, pks):

        fast_rows = []

        merged_df = pd.DataFrame(columns=st.session_state[VarEnum.sb_LOADED_DATAFRAME].columns)
        for cv in list_of_cluster_view:

            # rows that are not-selected must be added to the merged_df, but left in their original form
            # non_selected_rows = cv.records_df[~cv.records_df.index.isin(cv.selected_rows.index)]

            all_df = pd.merge(cv.records_df, cv.selected_rows, on=list(cv.selected_rows.columns),  how='left', indicator='exists')
            all_df['exists'] = np.where(all_df.exists == 'both', True, False)

            non_selected_rows = all_df[all_df['exists'] == False]
            for _, row in non_selected_rows.iterrows():
                fast_rows.append(row.to_dict())

            # merged_df = pd.concat([merged_df, non_selected_rows], ignore_index=True)

            # must only happen on the rows that are selected
            if st.session_state[f'merge_{cv.cluster_id}']:
                if st.session_state[f'dedup_{cv.cluster_id}'] == self.TEXT_DEDUP_TRUE:
                    # merged_df = pd.concat([merged_df, cv.new_row], ignore_index=True)
                    fast_rows.append(cv.new_row.to_dict())
                else:
                    for _, row in cv.selected_rows.iterrows():
                        for pk in pks:
                            cv.new_row[pk] = row[pk]
                        # merged_df = pd.concat([merged_df, row_to_add], ignore_index=True)
                        fast_rows.append(cv.new_row.to_dict())
            else:
                for _, row in cv.selected_rows.iterrows():
                    # merged_df = pd.concat([merged_df, row], ignore_index=True)
                    fast_rows.append(row.to_dict())
                    # merged_df.append(row, ignore_index=True)

        # a list comprehension that extract the value from the dict value
        for fr in fast_rows:
            for k,v in fr.items():
                if isinstance(v, dict):
                    for l, r in v.items():
                        fr[k] = r
                else:
                    fr[k] = v

        merged_df = pd.DataFrame(fast_rows)

        st.session_state[VarEnum.gb_CURRENT_STATE] = None
        if set(['_selectedRowNodeInfo', 'exists']) <= set(list(merged_df.columns)):
            merged_df = merged_df.drop(columns=['_selectedRowNodeInfo', 'exists'])

        if set(['z_minScore', 'z_maxScore', 'z_cluster']) <= set(list(merged_df.columns)):
            merged_df = merged_df.drop(columns=['z_minScore', 'z_maxScore', 'z_cluster'])

        st.session_state[VarEnum.sb_LOADED_DATAFRAME] = merged_df
        st.session_state[VarEnum.gb_CURRENT_STATE] = None

    def _create_cluster_card(self, idx, cv, pks):
        MIN_HEIGHT = 50
        MAX_HEIGHT = 500
        ROW_HEIGHT = 35
        
        cont_card = st.container()
        with cont_card:
            _ = st.checkbox('Apply changes!',value=True, key=f'merge_{cv.cluster_id}')
            col0, col1, col2 = st.columns([1,1,1])
            with col0:
                st.write(f"Confidence of this cluster: {cv.cluster_confidence}")
            with col1:
                st.write(f"Lowest similarity in this cluster: {cv.cluster_low}")
            
            with col2:
                st.write(f"Highest similarity in this cluster: {cv.cluster_high}")
                 
            gb1 = GridOptionsBuilder.from_dataframe(cv.records_df)
            gb1.configure_side_bar()
            gb1.configure_selection('multiple',use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True, pre_select_all_rows=True, header_checkbox=True)
            gb1.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gridOptions = gb1.build()
            data_clustercard = AgGrid(cv.records_df, gridOptions=gridOptions, enable_enterprise_modules=False, update_mode="SELECTION_CHANGED", height=min(MIN_HEIGHT + (len(cv.records_df) * ROW_HEIGHT), MAX_HEIGHT), key=f'before_{cv.cluster_id}')

            tmpList = []
            for e in data_clustercard['selected_rows']:
                tmpDict = {}
                for k in cv.records_df.columns:
                    tmpDict[k] = e[k]
                tmpList.append(tmpDict)

            cv.selected_rows = pd.DataFrame(tmpList)
            dedupe_check = st.radio('The selected records will be... ',(self.TEXT_DEDUP_FALSE, self.TEXT_DEDUP_TRUE), key=f'dedup_{cv.cluster_id}', horizontal = True)
            
            # AGGRID die wel editeerbaar is, met als suggestie de eerste van de selected_rows van hierboven
            gb2 = GridOptionsBuilder.from_dataframe(cv.new_row.drop(pks, axis=1) if dedupe_check == self.TEXT_DEDUP_FALSE else cv.new_row )
            gb2.configure_side_bar()
            gb2.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
            gridOptions2 = gb2.build()
            grid = AgGrid(cv.new_row.drop(pks, axis=1) if dedupe_check == self.TEXT_DEDUP_FALSE else cv.new_row ,update_mode="VALUE_CHANGED", gridOptions=gridOptions2, enable_enterprise_modules=False, height=min(MIN_HEIGHT + ROW_HEIGHT, MAX_HEIGHT))
            
            cv.set_new_row(grid["data"])

            customSpan = rf"""
            <span id="duplicateCardsFinder{idx}">
            </span>
            """
            st.markdown(customSpan,unsafe_allow_html=True)
            js = f'''<script>
            containerElement = window.parent.document.getElementById("duplicateCardsFinder{idx}").parentElement.parentElement.parentElement.parentElement.parentElement
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
        containerElement.setAttribute('id', 'containerDuplicateCards')
        </script>
        '''
        st.components.v1.html(js)

class ZinggClusterView:
    def __init__(self, cluster_id, cluster_confidence, records_df, new_row, cluster_low, cluster_high) -> None:
        self.cluster_id = cluster_id
        self.cluster_confidence = round(cluster_confidence, 4)
        self.records_df = records_df
        self.cluster_low = round(cluster_low, 4)
        self.cluster_high = round(cluster_high, 4)
        self.new_row = new_row
        self.selected_rows = records_df

    def set_new_row(self, new_row):
        # keep the values of self.new_row for columns that are not in new_row
        try:
            for col in self.new_row.columns:
                if col not in new_row.columns:
                    new_row[col] = self.new_row[col]
        except Exception as e:
            print(e)
        finally:
            # check if ['z_minScore', 'z_maxScore', 'z_cluster'] are present as columns in new_row, if they are delete them
            if 'z_minScore' in new_row.columns:
                del new_row['z_minScore']
            if 'z_maxScore' in new_row.columns:
                del new_row['z_maxScore']
            if 'z_cluster' in new_row.columns:
                del new_row['z_cluster']
            self.new_row = new_row
        
