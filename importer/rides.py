import incidents
import csv
from postgis import LineString
from datetime import datetime
from db_connection import DatabaseConnection
import filters
import map_match_service
import leg_service
import stop_service

def handle_ride_file(filename, cur):
    with open(filename, 'r') as f:
        incident_list = []
        ride = []
        split_found = False
        for line in f.readlines():
            if "======" in line:
                split_found = True
                continue
            if not split_found:
                incident_list.append(line)
            else:
                ride.append(line)
        incidents.handle_incidents(incident_list, filename, cur)
        handle_ride(ride, filename, cur)


def handle_ride(data, filename, cur):
    data = csv.DictReader(data[1:], delimiter=",")

    raw_coords = []
    accuracies = []
    timestamps = []

    for row in data:
        if row["lat"]:
            raw_coords.append([float(row["lon"]), float(row["lat"])])
            try:
                if row["acc"]:
                    accuracies.append(float(row["acc"]))
            except KeyError:
                return
            timestamps.append(datetime.utcfromtimestamp(int(row["timeStamp"]) / 1000))  # timeStamp is in Java TS Format
    ride = Ride(raw_coords, accuracies, timestamps)

    if len(ride.raw_coords) == 0:
        return

    ride = filters.apply_smoothing_filters(ride)

    if filters.apply_removal_filters(ride):
        return

    map_matched = map_match_service.map_match(ride)

    legs = leg_service.determine_legs(map_matched, cur)
    leg_service.update_legs(ride, legs, cur)

    stop_service.process_stops(ride, cur)

    ls = LineString(ride.raw_coords, srid=4326)
    filename = filename.split("/")[-1]

    try:
        cur.execute("""
            INSERT INTO public."SimRaAPI_ride" (geom, timestamps, legs, filename) VALUES (%s, %s, %s, %s)
        """, [ls, timestamps, [i[0] for i in legs], filename])
    except:
        print(f"Problem parsing {filename}")
        raise Exception("Can not parse ride!")


if __name__ == '__main__':
    filepath = "../csvdata/Berlin/Rides/VM2_-351907452"
    with DatabaseConnection() as cur:
        handle_ride_file(filepath, cur)


class Ride:
    def __init__(self, raw_coords, accuracies, timestamps):
        self.raw_coords = raw_coords
        self.raw_coords_filtered = None
        self.accuracies = accuracies
        self.timestamps = timestamps
        self.timestamps_filtered = None
