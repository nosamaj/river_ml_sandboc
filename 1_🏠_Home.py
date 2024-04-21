# Using streamlit libary licensed under MIT
# https://github.com/whitphx/streamlit
# https://github.com/whitphx/streamlit/blob/master/LICENSE
# Using data from https://environment.data.gov.uk under the Open Government Licence

import streamlit as st
import folium
import leafmap.foliumap as leafmap
import pandas as pd
import hydrology_explorer

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


###################
# Main body of app#
##################

df_level_stations = hydrology_explorer.get_open_stations(
    "2005-01-01", "2025-02-20", "*"
)
df_level_stations.rename({"@id": "id", "long": "lon"}, axis="columns", inplace=True)

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


with st.expander("About this app"):

    st.markdown(
        """
                
    This application will allow the user to explore the EA flooding API for
    
    - Rainfall data from the EA Gauges
    
    - River Level and Flow data 
    
    - Groundwater and tide data
    """
    )


with st.sidebar:
    st.title("EA Open Data Viewer")
    with st.form("my_form"):
        st.write("Select Station to view")
        station_name = st.selectbox(df_level_stations["label"])


col1, col2 = st.columns(2)

with col1:
    st.dataframe(data=df_level_stations_display, height=400)

with col2:
    create_map(
        lat=53.2, lon=-1.5, zoom_value=5, data=df_level_stations_display
    ).to_streamlit(height=400)

st.plotly_chart
