# Using streamlit libary licensed under MIT
# https://github.com/whitphx/streamlit
# https://github.com/whitphx/streamlit/blob/master/LICENSE
# Using data from https://environment.data.gov.uk under the Open Government Licence
import sys
sys.path.insert(0,'../utils')
import streamlit as st
import folium
import leafmap.foliumap as leafmap
import pandas as pd
from utils import hydrology_explorer

# Set page title icons and options for layout
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")


def replace_list_values(column: pd.Series) -> pd.Series:
    """
    Replaces values in a Pandas Series that are lists with the first element
    in the list.

    Args:
        column: A Pandas Series to apply the function to.

    Returns:
        A Pandas Series with lists replaced by their first element.
    """

    # Apply a function to each element in the column
    return column.apply(lambda x: x[0] if isinstance(x, list) else x)  # type: ignore


def get_measures(station: str) -> pd.DataFrame:
    """
    Retrieves the measures associated with a given station from a dataframe.

    Args:
        station (str): The label of the station for which to retrieve measures.

    Returns:
        pd.DataFrame: A Pandas DataFrame representing the measures associated
            with the given station.
    """
    df_measures = hydrology_explorer.measures_from_station(df_level_stations, station)
    return df_measures



def create_map(
    lat: float, lon: float, zoom_value: int, data: pd.DataFrame
) -> folium.Map:
    """
    Create a folium map with markers for the stations in the data.

    Args:
        lat: Latitude of the map centre.
        lon: Longitude of the map centre.
        zoom_value: The initial zoom level of the map.
        data: A Pandas DataFrame of stations with columns 'lat' and 'lon'.

    Returns:
        A Folium Map object with markers added for each station.
    """
    m = leafmap.Map(center=[lat, lon], zoom=zoom_value)
    # Create a map with a single marker
    stations = data

    m.add_points_from_xy(
        stations,
        x="lon",
        y="lat",
        # color_column='riverName',  # uncomment to add legend
        # icon_names=['gear', 'map', 'leaf', 'globe'],  # uncomment to add icons
        # spin=True,  # uncomment to add spinning icons
        add_legend=True,  # set to False to remove legend
    )

    return m
@st.cache_data
def get_stations(start_date: str, end_date: str, property: str) -> pd.DataFrame:
    df_level_stations = hydrology_explorer.get_open_stations(
    "2005-01-01", "2025-02-20", "*"
    )
    df_level_stations.rename({"@id": "id", "long": "lon"}, axis="columns", inplace=True)
    return df_level_stations

def update_station(selected_option):
  st.session_state["station_name"] = selected_option

###################
# Main body of app#
##################

df_level_stations = get_stations(
    "2005-01-01", "2025-02-20", "*"
)

with st.sidebar:
    st.title("EA Open Data Viewer")

    station_name = st.selectbox('Station Name',df_level_stations["label"])
    

df_rainfall_sites = pd.DataFrame()

if station_name not in st.session_state:
    st.session_state[station_name] = ""

if df_rainfall_sites not in st.session_state:
    st.session_state[df_rainfall_sites] = pd.DataFrame()





for col in [
    "lat",
    "lon",
    "easting",
    "northing",
    "riverName",
]:
    if df_level_stations[col].apply(lambda x: isinstance(x, list)).any():
        df_level_stations[col] = replace_list_values(df_level_stations[col])

        # df_level_stations[col] = df_level_stations[col].astype(float)
df_level_stations_display = df_level_stations[
    [
        "label",
        "riverName",
        "lat",
        "lon",
        "easting",
        "northing",
        "stationReference",
        "dateOpened",
        "catchmentArea",
        "id",
        "colocatedStation",
    ]
]



station_lat = df_level_stations[df_level_stations["label"] == station_name]["lat"].values[0]
station_lon = df_level_stations[df_level_stations["label"] == station_name]["lon"].values[0]

station_easting = df_level_stations[df_level_stations["label"] == station_name]["easting"].values[0]
station_northing = df_level_stations[df_level_stations["label"] == station_name]["northing"].values[0]

#get all rainfall sites within 8km 
df_rainfall_sites = hydrology_explorer.get_rainfall(
    station_easting, station_northing, 8000  
)
st.session_state['df_rainfall_sites'] = df_rainfall_sites

col1, col2 = st.columns(2)

with col1:
    st.dataframe(data=df_level_stations_display, height=400)

with col2:
    create_map(
        lat=station_lat, lon=station_lon, zoom_value=11, data=df_level_stations_display
    ).to_streamlit(height=400)

measures = hydrology_explorer.measures_from_station(df_level_stations,station_name)
st.dataframe(measures)
st.dataframe(df_rainfall_sites)