import incidents
import csv
from postgis import LineString
from datetime import date
from db_connection import DatabaseConnection


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

    ride = []
    timestamps = []

    for row in data:
        if row["lat"]:
            ride.append([row["lon"], row["lat"]])
            timestamps.append(date.fromtimestamp(int(row["timeStamp"]) / 1000))     # timeStamp is in Java TS Format

    if len(ride) == 0:
        return

    ls = LineString(ride, srid=4326)
    filename = filename.split("/")[-1]

    try:
        cur.execute("""
            INSERT INTO public."SimRaAPI_ride" (geom, timestamps, filename) VALUES (%s, %s, %s)
        """, [ls, timestamps, filename])
    except:
        print(f"Problem parsing {filename}")
        raise Exception("Can't parse ride!")


if __name__ == '__main__':
    filepath = "../csvdata/Berlin/Rides/VM2_-351907452"
    with DatabaseConnection() as cur:
        handle_ride_file(filepath, cur)
