_DATASET_URL = "https://github.com/C10udburst/wawbus-data/raw/master/bus-data/{}.gzip"
_TIMETABLE_URL = "https://github.com/C10udburst/wawbus-data/raw/master/timetables/timetable-{}.gzip"
_STOPS_URL = "https://github.com/C10udburst/wawbus-data/raw/master/stops.gzip"

# Source: https://pl.wikipedia.org/wiki/Autobusy_miejskie_w_Warszawie
BUS_LENGTH = 18  # biggest ZTM bus is 18m long
MAX_SPEED = 90  # maximum physically possible speed for a bus

CRS = "EPSG:4326"
M_TO_KM = 1 / 1000
