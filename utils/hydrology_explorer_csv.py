import requests
import pandas as pd
import json
from io import StringIO
from typing import List, Dict

# API DOCS https://environment.data.gov.uk/hydrology/doc/reference#batch-api

base_uri = "http://environment.data.gov.uk/"

# open_stations = "/hydrology/id/open/stations?from=2020-05-10&to=2020-08-10"

# flow_stations_per_river = "/hydrology/id/stations?observedProperty=waterFlow&riverName=River+Exe"

# stations_km_from_point = "/hydrology/id/stations?lat=50.5&long=-4.15&dist=3"

# #/hydrology/id/measures/{measure}/readings
# get_data = "/hydrology/id/measures/bf679fd0-8d8f-4815-a569-ec798d81f324-flow-i-900-m3s-qualified/readings?mineq-date=2021-01-01&max-date=2021-01-08"

# list_timeseries_per_sation = "/hydrology/id/stations/{station}/measures"
# [json] [html]


def get_open_stations(start_date: str, end_date: str) -> pd.DataFrame:
    """Get a list of open hydrology stations between a start and end date.

    This function returns a pandas DataFrame containing information about open
    hydrology stations that have data for the given property (e.g. water level,
    rainfall).

    Args:
        start_date (str): Start date for which to get data (format: YYYY-MM-DD).
        end_date (str): End date for which to get data (format: YYYY-MM-DD).
        property (str): Property for which to get data (e.g. 'waterLevel',
            'rainfall').

    Returns:
        pandas.DataFrame: A dataframe containing information about open
            hydrology stations.
    """
    stations = requests.get(
        base_uri
        + f"/hydrology/id/open/stations.csv?from={start_date}&to={end_date}&observedProperty={property}&_limit=100000"
    )
 
    csv_string = stations.text
    df_stations = pd.read_csv(StringIO(csv_string))
    return df_stations


def get_measures_station_id(station_id: str) -> pd.DataFrame:
    """
    Get a list of measures for a given station.

    This function returns a requests.Response object containing information
    about the measures associated with a given station.

    Args:
        station (str): The label of the station for which to retrieve measures.

    Returns:
        requests.Response: A requests.Response object containing information
            about the measures associated with the given station.
    """
    measures = requests.get(base_uri + f"hydrology/id/stations/{station_id}/measures.csv")
    csv_string = measures.text
    df_measures = pd.read_csv(StringIO(csv_string))
    return df_measures


def measure_ids_from_stations_df(station_name: str, stations_df: pd.DataFrame) -> List[str]:
    """
    Get a list of measure IDs associated with a station from a DataFrame.

    Args:
        station_name (str): The name of the station for which to retrieve measure IDs.
        stations_df (pd.DataFrame): DataFrame containing station information.

    Returns:
        List[str]: A list of measure IDs associated with the given station.
    """
    #get the value of measures from the df where the label is the station name
    measures_str = stations_df[stations_df["label"] == station_name]["measures"].values[0]
    # split string into list of substrings based on a | delimiter
    #measures_str = measures_str.replace("|",";")
    print(measures_str)
    if "|" in measures_str:
        
        measures_list = measures_str.split("|")
        return measures_list
    #if there are is just one measure return it as a list
    else:
        measures_list =[measures_str]
        return measures_list


def get_readings(
    start_date: str, end_date: str, measure_id: str
) -> requests.Response:
    """
    Get readings between a start and end date for a given measure.

    This function returns a requests.Response object containing the readings
    between the given start and end dates for the given measure.

    Args:
        start_date (str): Start date for which to get data (format: YYYY-MM-DD).
        end_date (str): End date for which to get data (format: YYYY-MM-DD).
        measure_id (str): ID of the measure for which to retrieve readings.

    Returns:
        requests.Response: A requests.Response object containing the readings
            between the given start and end dates for the given measure.
    """
    readings = requests.get(
        f"{measure_id}/readings.csv?mineq-date={start_date}&max-date={end_date}&_limit=1990000"
    )
    csv_string = readings.text
    df_readings = pd.read_csv(StringIO(csv_string))

    return df_readings


def json_to_dataframe(json_response):
    """
    Converts a JSON response from an API into a Pandas DataFrame.

    Args:
        json_response: A dictionary or list containing the JSON data.

    Returns:
        A Pandas DataFrame representing the JSON data.
    """

    # Check if the response is a list or dictionary
    if isinstance(json_response, list):
        # If it's a list, assume each element is a dictionary representing a data point
        data_list = []
        for item in json_response:
            data_list.append(pd.Series(item))
        return pd.DataFrame(data_list)
    else:
        # If it's a dictionary, assume it's the top-level structure of the data
        return pd.DataFrame(json_response)


def measures_from_station(stations_df: pd.DataFrame,
                          station_label: str) -> pd.DataFrame:
    """
    Retrieves the measures associated with a given station from a dataframe.

    Args:
        stations_df: A Pandas DataFrame containing information about hydrology
            stations.
        station_label: The label of the station for which to retrieve measures.

    Returns:
        A Pandas DataFrame representing the measures associated with the given
        station.
    """
    row_number = stations_df[stations_df["label"] == station_label].index[0]
    measures = pd.json_normalize(stations_df.loc[row_number, "measures"])
    return measures


def get_rainfall(location_easting: float,
                 location_northing: float,
                 distance: float) -> pd.DataFrame:
    """
    Returns a rainfall hydrology stations that are within a given distance
    of a given location.

    Args:
        location_easting: The easting coordinate of the reference location.
        location_northing: The northing coordinate of the reference location.
        distance: The maximum distance from the reference location (in metres).

    Returns:
        A Pandas DataFrame containing information about the subset of stations
        that are within the given distance of the reference location.
    """
    stations_df = get_open_stations("1970-01-01", "2025-02-20", "rainfall")
    rainfall_sites = stations_df[
        (abs(stations_df["easting"] - location_easting) <= distance) &
        (abs(stations_df["northing"] - location_northing) <= distance)
    ]

    return rainfall_sites


if __name__ == "__main__":
    df_level_stations= get_open_stations("2005-01-01", "2025-02-20", "waterLevel")
    df_raingauges = get_open_stations("2005-01-01", "2025-02-20", "rainfall")
    #raingauges = pd.json_normalize(raingauges.json()["items"])

    # Get the row number as an index object
    #easting = df_level_stations[row_number, "easting"]
    #northing = df_level_stations.loc[row_number, "northing"]


    # measures = measure_ids_from_stations_df("Packington", df_level_stations)
    # for measure in measures:
    #     readings = get_readings("1900-01-01", "2024-12-31", measure)


    #local_gauges = get_rainfall(
    #    raingauges, easting, northing, 5000
    #)  # 5km from Packington

    #df_readings.to_parquet("packington.parquet")
    #df_level_stations.to_csv("level_stations.csv", index=False)
    #df_raingauges.to_csv("gauges.csv", index=False)
    #measures.to_csv("measures.csv", index=False)
    #local_gauges.to_csv("local_gauges.csv", index=False)

###########
#only nneed this bit if refeshing the list - better to use local copy
    df_all_stations = get_open_stations("2000-01-03", "2025-02-20", "*")
    
    #df_all_stations.to_parquet("..\datasets\openstations_copy.parquet")
    # #querry df_all_stations for label and riverName where either contain "hilden brook"
    # ######
    
    
############

    df_all_stations = pd.read_parquet("..\datasets\openstations_copy.parquet")

    

    df_mease = df_all_stations[(df_all_stations['riverName'].str.lower() == 'mease') | (df_all_stations['riverName'].str.lower() == 'river mease')]
   

    mease_station_names = df_mease['label'].to_list()



    measures_dict = {}

    for station in mease_station_names:
        measures_dict[station] = measure_ids_from_stations_df(station, df_mease)
    
    for station,measures in measures_dict.items():
        print(measures)
        i=0
        for measure in measures:
            print(measure)
            measure_name = measure.split("/")[-1]
            df = get_readings("1970-01-01","2025-01-01",measure)
            df.to_parquet(f"../datasets/River Mease/{station}-{measure_name}.parquet")
            i+=1

    print(measures_dict)
    
