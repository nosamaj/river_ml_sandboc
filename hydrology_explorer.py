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


def get_open_stations(start_date, end_date,property):
    stations = requests.get(
        base_uri
        + f"/hydrology/id/open/stations.json?from={start_date}&to={end_date}&observedProperty={property}&_limit=100000"
    )
    print(
        base_uri + f"/hydrology/id/open/stations.json?from={start_date}&to={end_date}"
    )
    return stations


def get_measures(station):
    measures = requests.get(base_uri + f"hydrology/id/stations/{station}/measures.json")
    return measures


def get_readings(start_date, end_date, measure_id):
    readings = requests.get(
        f"{measure_id}/readings.json?mineq-date={start_date}&max-date={end_date}&_limit=1890000"
    )

    print(
        f"{measure_id}/readings.json?mineq-date={start_date}&max-date={end_date}&_limit=1890000"
    )

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


def measures_from_station(stations_df, station_label):
    row_number = stations_df[stations["label"] == station_label].index[0]
    measures = pd.json_normalize(data["items"][row_number]["measures"])
    return measures


def get_rainfall(stations_df, location_easting,location_northing, distance):
    rainfall_sites = stations_df[
    (abs(stations_df["easting"] - location_easting) <= distance) &
    (abs(stations_df["northing"] - location_northing)<= distance)
    ]
        
    return rainfall_sites


if __name__ == "__main__":
    open = get_open_stations("2005-01-01", "2025-02-20","waterLevel")
    data = open.json()
    print(data["items"])
    stations = pd.json_normalize(data["items"])
    raingauges = get_open_stations("2005-01-01", "2025-02-20","rainfall")
    raingauges = raingauges.json()
    raingauges = pd.json_normalize(raingauges["items"])
    # Get the row numbr as an index object
    row_number = stations[stations["label"] == "Packington"].index[0]
    easting = stations[stations["label"] == "Packington"]["easting"].values[0]
    northing = stations[stations["label"] == "Packington"]["northing"].values[0]
    measures = measures_from_station(stations, "Packington")
    # Print the row number
    # print(row_numbe-*

    readings = get_readings("1900-01-01", "2024-12-31", measures.loc[1]["@id"])
    readings = readings.json()
    df_readings = pd.json_normalize(readings["items"])

    local_gauges = get_rainfall(raingauges,easting,northing,5000)


    df_readings.to_parquet("packington.parquet")
    stations.to_csv("stations.csv")
    raingauges.to_csv("gauges.csv")
    measures.to_csv("measures.csv")
