from math import radians, cos, sin, asin, sqrt

import numpy as np


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees).
    Source: https://stackoverflow.com/a/4913653
    :param lon1: longitude of point 1
    :param lat1: latitude of point 1
    :param lon2: longitude of point 2
    :param lat2: latitude of point 2
    :return: distance in kilometers
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


# %%
def speed(row):
    """
    Pandas UDF to calculate speed from row.
    Assumptions:
        - Used internally in WawBus class
        - The vehicle is moving in a straight line between two points
    """
    if row['NextLon'] is np.nan:
        return None
    if row['NextTime'] == row['Time']:
        return None
    return haversine(row['Lon'], row['Lat'], row['NextLon'], row['NextLat']) / (
            (row['NextTime'] - row['Time']) / np.timedelta64(1, 'h')
    )