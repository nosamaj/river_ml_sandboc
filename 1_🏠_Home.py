import streamlit as st
#import utils.db_utils as db_utils
#import utils.fetcharchive as fetcharchive
#import utils.create_db_tables as create_db_tables
import folium
import leafmap.foliumap as leafmap

import hydrology_explorer


st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout='wide'
)

def replace_list_values(column):
    return column.apply(lambda x: x[0] if isinstance(x, list) else x)

df_level_stations = hydrology_explorer.get_open_stations("2005-01-01", "2025-02-20","*")
df_level_stations.rename({'@id':'id','long':'lon'},axis='columns',inplace=True)

for col in ['lat','lon','easting','northing','riverName',]:
    if df_level_stations[col].apply(lambda x: isinstance(x, list)).any():
        df_level_stations[col] = replace_list_values(df_level_stations[col])

        #df_level_stations[col] = df_level_stations[col].astype(float)
df_level_stations_display = df_level_stations[['label','riverName','lat','lon','easting','northing','stationReference','dateOpened','catchmentArea','id','colocatedStation']]

with st.expander("About this app"):

    st.markdown('''
                
    This application will allow the user to explore the EA flooding API for
    
    - Rainfall data from the EA Gauges
    
    - River Level and Flow data 
    
    - Groundwater and tide data
    ''')
    
def get_measures(station):
    df_measures = hydrology_explorer.measures_from_station(df_level_stations, station)
    return df_measures

with st.sidebar:
    st.title('EA Open Data Viewer')
    with st.form("my_form"):
        st.write("Select Station to view)
        station_name = st.selectbox(
            df_level_stations['label']
        )

m = leafmap.Map(center=[53.1, -3], zoom=7)      
stations = df_level_stations_display

    
m.add_points_from_xy(
    stations,
    x="lon",
    y="lat",
    #color_column='riverName',
    #icon_names=['gear', 'map', 'leaf', 'globe'],
    #spin=True,
    add_legend=True
)

col1, col2 = st.columns(2)

with col1:
    st.dataframe(data=df_level_stations_display,height=400)

with col2:
    m.to_streamlit(height=400)

st.plotly_chart