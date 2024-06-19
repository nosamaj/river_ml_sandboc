import requests
import pandas as pd
import json

# API DOCS https://environment.data.gov.uk/hydrology/doc/reference#batch-api

base_uri = "http://environment.data.gov.uk/"

# open_stations = "/hydrology/id/open/stations?from=2020-05-10&to=2020-08-10"

# flow_stations_per_river = "/hydrology/id/stations?observedProperty=waterFlow&riverName=River+Exe"

# stations_km_from_point = "/hydrology/id/stations?lat=50.5&long=-4.15&dist=3"

# #/hydrology/id/measures/{measure}/readings
# get_data = "/hydrology/id/measures/bf679fd0-8d8f-4815-a569-ec798d81f324-flow-i-900-m3s-qualified/readings?mineq-date=2021-01-01&max-date=2021-01-08"

# list_timeseries_per_sation = "/hydrology/id/stations/{station}/measures"
# [json] [html]


def get_open_stations(start_date: str, end_date: str, property: str) -> pd.DataFrame:
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
        + f"/hydrology/id/open/stations.json?from={start_date}&to={end_date}&observedProperty={property}&_limit=100000"
    )
    print(
        base_uri
        + f"/hydrology/id/open/stations.json?from={start_date}&to={end_date}"
    )

    df_stations = pd.json_normalize(stations.json()["items"])

    return df_stations


def get_measures(station: str) -> requests.Response:
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
    measures = requests.get(base_uri + f"hydrology/id/stations/{station}/measures.json")
    return measures



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
        f"{measure_id}/readings.json?mineq-date={start_date}&max-date={end_date}&_limit=1890000"
    )
    readings = pd.json_normalize(readings.json()["items"])

    # print(
    #     f"{measure_id}/readings.json?mineq-date={start_date}&max-date={end_date}&_limit=1890000"
    # )

    return readings


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
    #
    #data = open.json()
    df_stations = get_open_stations("2005-01-01", "2025-02-20", "*")

    df_raingauges = get_open_stations("2005-01-01", "2025-02-20", "rainfall")
 
    
    # Get the row number as an index object
    row_number = df_stations[df_stations["label"] == "Packington"].index[0]
    easting = df_stations.loc[row_number, "easting"]
    northing = df_stations.loc[row_number, "northing"]
    df_measures = measures_from_station(df_stations, "Packington")

    readings = get_readings("1900-01-01", "2024-12-31", df_measures.loc[1, "@id"])
    df_readings = pd.json_normalize(readings.json()["items"])

    local_gauges = get_rainfall(
        easting, northing, 5000
    )  # 5km from Packington

    df_readings = readings
    
    

    # df_readings.to_parquet("packington.parquet")
    # df_stations.to_csv("stations.csv", index=False)
    # df_raingauges.to_csv("gauges.csv", index=False)
    # df_measures.to_csv("measures.csv", index=False)
    # local_gauges.to_csv("local_gauges.csv", index=False)

    
    df_frome = df_stations[(df_stations['riverName'].str.lower() == 'frome') | (df_stations['riverName'].str.lower() == 'somerset frome')]
    
    frome_labels = df_frome['label'].to_list()
   
    for label in frome_labels:
        df_measures = measures_from_station(df_frome, label)
        for index,row in df_measures.iterrows():
            readings = get_readings("1900-01-01", "2024-12-31", row["@id"])
            readings.to_parquet(f"../datasets/River frome/{label}-{row['parameter']}-{row['period']}.parquet")
        #print(df_measures.head)