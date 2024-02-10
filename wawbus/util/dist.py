from math import radians, cos, sin, asin, sqrt

import numpy as np


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees).
    Source: https://stackoverflow.com/a/4913653

    Args:
        lon1 (float): longitude of point 1
        lat1 (float): latitude of point 1
        lon2 (float): longitude of point 2
        lat2 (float): latitude of point 2

    Returns:
        distance in kilometers
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles.
    return c * r


# %%
def speed(row):
    """
    Pandas UDF to calculate speed from row.

    Assumptions:
        Used internally in WawBus class
        The vehicle is moving in a straight line between two points
    """
    if row['NextLon'] is np.nan:
        return None
    if row['NextTime'] == row['Time']:
        return None
    return haversine(row['Lon'], row['Lat'],
                     row['NextLon'], row['NextLat']) / (
            (row['NextTime'] - row['Time']) / np.timedelta64(1, 'h')
    )


def stop_dist(row):
    """
    Pandas UDF to calculate distance from stop.

    Assumptions:
        Used internally in WawBus class
        Row contains 'Lon', 'Lat', 'dlug_geo', 'szer_geo'
    """
    return haversine(row['Lon'], row['Lat'], row['dlug_geo'], row['szer_geo'])
