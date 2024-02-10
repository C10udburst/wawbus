"""
Attributes:
    BUS_LENGTH (int): biggest ZTM bus is 18m long, Source: https://pl.wikipedia.org/wiki/Autobusy_miejskie_w_Warszawie
    MAX_SPEED (int): maximum physically possible speed for a bus,
        Source: https://pl.wikipedia.org/wiki/Autobusy_miejskie_w_Warszawie
    M_TO_KM (float): meters to kilometers
    CRS (str): Coordinate Reference System used by the UM API
"""

_DATASET_URL = "https://github.com/C10udburst/wawbus-data/raw/master/bus-data/{}.gzip"
_TIMETABLE_URL = "https://github.com/C10udburst/wawbus-data/raw/master/timetables/timetable-{}.gzip"
_STOPS_URL = "https://github.com/C10udburst/wawbus-data/raw/master/stops.gzip"

BUS_LENGTH = 18
MAX_SPEED = 95

CRS = "EPSG:4326"
M_TO_KM = 1 / 1000
