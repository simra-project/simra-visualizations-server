# IMPORT_DIRECTORY = "../csvdata/EichwaldeNew/ZES_Experimentell"
IMPORT_DIRECTORY = "../csvdata"
DB_HOST = "127.0.0.1"
DB_NAME = "simra"
DB_USER = "simra"
DB_PASSWORD = "simra12345simra"
DB_PORT = 5432

MIN_ACCURACY = 10
RDP_EPSILON = 0.0000001

MIN_RIDE_DISTANCE = 200  # in meters
MIN_RIDE_DURATION = 3 * 60  # in seconds
MAX_RIDE_AVG_SPEED = 40  # in km/h
MIN_DISTANCE_TO_COVER_IN_5_MIN = 100  # in meters

COVERED_DISTANCE_INSIDE_STOP_THRESHOLD = 0.5  # in meters
DISTANCE_TO_JUNCTION_THRESHOLD = 30  # in meters

COVERED_DISTANCE_INSIDE_STOP_FOR_VELOCITY_THRESHOLD = 4.2  # in meters. ≈ 5km/h with a resolution of 1coord/3secs