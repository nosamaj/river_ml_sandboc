import streamlit as st
#import utils.db_utils as db_utils
import ea_api_request
#import utils.fetcharchive as fetcharchive
#import utils.create_db_tables as create_db_tables



st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout='wide'
)

    

st.title('EA Open Data Viewer')

st.markdown('''This application will allow the user to explore the EA flooding API for
- Rainfall data from the EA Gauges
- River Level and Flow data 
- Groundwater and tide data.

The options available are to see a map of the available sites, graph data for comparision and explore a statistical analaysis of data.''')
