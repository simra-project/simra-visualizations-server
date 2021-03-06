import incidents
import csv
from postgis import LineString, Point
from datetime import datetime
from db_connection import DatabaseConnection
import filters
import map_match_service
import leg_service
import stop_service
import velocity_service
import surface_quality_service
import settings


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
        phone_loc, incident_locs = incidents.handle_incidents(incident_list, filename, cur)
        if settings.GET_ALL_SURFACE_SCORES:
            phone_loc = "1"
        handle_ride(ride, filename, cur, phone_loc, incident_locs)


def handle_ride(data, filename, cur, phone_loc, incident_locs):
    data = csv.DictReader(data[1:], delimiter=",")

    raw_coords = []
    accuracies = []
    timestamps = []
    accelerations = []

    for row in data:
        if row["lat"]:
            raw_coords.append([float(row["lon"]), float(row["lat"])])
            try:
                if row["acc"]:
                    if float(row["acc"]) > 100.0:  # ride goes to trash
                        print("Ride is filtered due to accuracies > 100m")
                        return
                    accuracies.append(float(row["acc"]))
            except KeyError:
                return
            timestamps.append(datetime.utcfromtimestamp(int(row["timeStamp"]) / 1000))  # timeStamp is in Java TS Format
        try:
            if row["X"]:
                accelerations.append((float(row["X"]), float(row["Y"]), float(row["Z"]),
                                      datetime.utcfromtimestamp(int(row["timeStamp"]) / 1000), raw_coords[-1]))
        except TypeError:
            return
    ride = Ride(raw_coords, accuracies, timestamps)

    if len(ride.raw_coords) == 0:
        print("Ride is filtered due to len(coords) == 0")
        return

    if is_teleportation(ride.timestamps):
        print("Ride is filtered due to teleportation")
        return

    IRI, ride_sections_surface = surface_quality_service.process_surface(ride, accelerations)
    ride_sections_velocity = velocity_service.process_velocity(ride)

    ride = filters.apply_smoothing_filters(ride)
    if filters.apply_removal_filters(ride):
        return

    map_matched = map_match_service.map_match(ride)
    if len(map_matched) == 0:
        return

    legs = leg_service.determine_legs(map_matched, cur)
    leg_service.update_legs(ride, legs, cur, IRI, phone_loc, ride_sections_velocity, incident_locs)

    stop_service.process_stops(ride, legs, cur)

    ls = LineString(ride.raw_coords_filtered, srid=4326)
    filename = filename.split("/")[-1]

    start = Point(ride.raw_coords_filtered[0], srid=4326)
    end = Point(ride.raw_coords_filtered[-1], srid=4326)
    if phone_loc == 1 or phone_loc == "1":  # Handlebar
        print("Phone is on Handlebar, finding road surface quality")
        try:
            cur.executemany("""
    INSERT INTO public."SimRaAPI_ridesegmentsurface" (geom, score) VALUES (%s, %s)
            """, ride_sections_surface)
        except Exception as e:
            print("Can't create surface ride segments.")
            raise (e)
    try:
        cur.executemany("""
    INSERT INTO public."SimRaAPI_ridesegmentvelocity" (geom, velocity) VALUES (%s, %s)
                """, list(map(lambda x: (LineString(x[0], srid=4326), x[2]), ride_sections_velocity)))
    except Exception as e:
        print("Can't create velocity ride segments.")
        raise (e)
    try:
        cur.execute("""
            INSERT INTO public."SimRaAPI_ride" (geom, timestamps, legs, filename, "start", "end") VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """, [ls, timestamps, [i[0] for i in legs], filename, start, end])
        ride_id = cur.fetchone()[0]
        incidents.update_ride_ids([i[2] for i in incident_locs], ride_id, cur)

    except:
        print(f"Problem parsing {filename}")
        raise Exception("Can not parse ride!")


if __name__ == '__main__':
    filepath = "../csvdata/Berlin/Rides/VM2_-351907452"
    with DatabaseConnection() as cur:
        handle_ride_file(filepath, cur)


def is_teleportation(timestamps):
    for i, t in enumerate(timestamps):
        if i + 1 < len(timestamps):
            if (timestamps[i + 1] - timestamps[i]).seconds > 20:
                return True
    return False


class Ride:
    def __init__(self, raw_coords, accuracies, timestamps):
        self.raw_coords = raw_coords
        self.raw_coords_filtered = None
        self.accuracies = accuracies
        self.timestamps = timestamps
        self.timestamps_filtered = None
