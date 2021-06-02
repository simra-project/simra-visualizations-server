"""Application logic to import ride entities from a CSV file.

Methods
-------
handle_ride_file()
    Splits up a CSV file into incidents and ride coordinates and
    calls the respective methods to process them further.
handle_ride()
    Reads all relevant data from a CSV file and persists the corresponding
    data regarding the ride in the database.
is_teleportation()

Classes
-------
Ride
    A class used to represent a bicycle ride.
"""

import incidents
import csv
import os
from postgis import LineString, Point
from datetime import datetime
from db_connection import DatabaseConnection
import filters
import map_match_service
import shortest_path_service
import leg_service
import stop_service
import velocity_service
import surface_quality_service
import settings


def handle_ride_file(filename, cur):
    """Splits up a CSV file into incidents and ride coordinates and
    calls the respective methods to process them further.

    Parameters
    ----------
    filename : str
        Name of the CSV file the ride is saved in.
    cur : DatabaseConnection
    """

    with open(filename, "r") as f:
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
        phone_loc, incident_locs = incidents.handle_incidents(
            incident_list, filename, cur
        )
        if settings.GET_ALL_SURFACE_SCORES:
            phone_loc = "1"
        handle_ride(ride, filename, cur, phone_loc, incident_locs)


def handle_ride(data, filename, cur, phone_loc, incident_locs):
    """Reads all relevant data from a CSV file and persists the corresponding
    data regarding the ride in the database.

    Parameters
    ----------
    data : str[ ]
        Data entries of the CSV file describing the ride.
    filename : str
        Name of the CSV file where the ride is saved in.
    cur : DatabaseConnection
    phone_loc : bool
        1, if the phone was attached to the handlebar, 0 otherwise.
        If 1, street quality can be calculated from the sensor data.
    incident_locs :
        TODO:
    """

    data = csv.DictReader(data[1:], delimiter=",")

    raw_coords = []
    accuracies = []
    timestamps = []
    accelerations = []

    # Process the CSV file line by line and save into the variable ride
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
            # timeStamp is in Java TS Format
            timestamps.append(datetime.utcfromtimestamp(int(row["timeStamp"]) / 1000))
        try:
            if row["X"]:
                accelerations.append(
                    (
                        float(row["X"]),
                        float(row["Y"]),
                        float(row["Z"]),
                        datetime.utcfromtimestamp(int(row["timeStamp"]) / 1000),
                        raw_coords[-1],
                    )
                )
        except Exception:  # TypeError:
            return
    ride = Ride(raw_coords, accuracies, timestamps)

    # Start of filter pipeline =======>
    if len(ride.raw_coords) == 0:
        settings.logging.info("Ride is filtered due to len(coords) == 0")
        return

    if is_teleportation(ride.timestamps):
        settings.logging.info("Ride is filtered due to teleportation")
        return

    IRI, ride_sections_surface = surface_quality_service.process_surface(
        ride, accelerations
    )
    ride_sections_velocity = velocity_service.process_velocity(ride)

    ride = filters.apply_smoothing_filters(ride)
    if filters.apply_removal_filters(ride):
        return
    # <------- End of filter pipeline

    # Map match the data
    map_matched = map_match_service.map_match(ride)
    if len(map_matched) == 0:
        return

    # Determine remaining attributes
    ls = LineString(ride.raw_coords_filtered, srid=4326)
    filename = filename.split("/")[-1]

    start = Point(ride.raw_coords_filtered[0], srid=4326)
    end = Point(ride.raw_coords_filtered[-1], srid=4326)

    # Start of entity processing pipeline =======>
    # Process shortest path
    sp = shortest_path_service.query_shortest_path_server(start, end)
    shortest_path = LineString(sp, srid=4326)

    # Process legs from the rides data
    # Get set of OSM legs blonging to the shortest path of a trajectory
    shortest_path_legs = leg_service.determine_legs(sp, cur)
    # Get set of OSM legs belonging to a ride
    legs = leg_service.determine_legs(map_matched, cur)
    leg_service.update_legs(
        ride,
        legs,
        shortest_path_legs,
        cur,
        IRI,
        phone_loc,
        ride_sections_velocity,
        incident_locs,
    )

    # Process trajectory stops
    stop_service.process_stops(ride, legs, cur)

    # Create surface ride segments
    if phone_loc == 1 or phone_loc == "1":  # Handlebar
        settings.logging.info("Phone is on Handlebar, finding road surface quality")
        try:
            cur.executemany(
                """
    INSERT INTO public."SimRaAPI_ridesegmentsurface" (geom, score) VALUES (%s, %s)
            """,
                ride_sections_surface,
            )
        except Exception as e:
            settings.logging.exception("Can't create surface ride segments.")
            raise (e)

    # Create velocity ride segments
    try:
        cur.executemany(
            """
    INSERT INTO public."SimRaAPI_ridesegmentvelocity" (geom, velocity) VALUES (%s, %s)
                """,
            list(
                map(
                    lambda x: (LineString(x[0], srid=4326), x[2]),
                    ride_sections_velocity,
                )
            ),
        )
    except Exception as e:
        settings.logging.exception("Can't create velocity ride segments.")
        raise (e)

    # Process street segement popularity
    # TODO: Process street segment popularity in a service by calculating some score or so. Maybe
    # just do it inside the leg_service
    # <------- End of entity processing pipeline

    # Save the ride into the database
    try:
        cur.execute(
            """
            INSERT INTO public."SimRaAPI_ride" (geom, shortest_path, timestamps, legs, filename, "start", "end") VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """,
            [ls, shortest_path, timestamps, [i[0] for i in legs], filename, start, end],
        )
        ride_id = cur.fetchone()[0]
        incidents.update_ride_ids([i[2] for i in incident_locs], ride_id, cur)

    except:
        settings.logging.exception(f"Problem parsing {filename}")
        raise Exception("Can not parse ride!")


def is_teleportation(timestamps):
    """
    Parameters
    ----------
    timestamps : datetime[ ]
        Time stamps of coordinate measurements of the ride.

    Returns
    -------
    bool
        Whether the users phone 'teleported' during the ride.
    """

    for i, t in enumerate(timestamps):
        if i + 1 < len(timestamps):
            if (timestamps[i + 1] - timestamps[i]).seconds > 20:
                return True
    return False


class Ride:
    """A class used to represent a bicycle ride."""

    def __init__(self, raw_coords, accuracies, timestamps):
        """
        Parameters
        ----------
        raw_coords
            The coordinates of the trajectory.
        accuracies
        timestamps
        """
        self.raw_coords = raw_coords
        self.raw_coords_filtered = None
        self.accuracies = accuracies
        self.timestamps = timestamps
        self.timestamps_filtered = None


if __name__ == "__main__":
    """Executed when invoked directly. Only for testing purposes.

    Attention: Will result in multiple database entries for the same
    ride if executed more than once!
    """

    dirname = os.path.dirname(os.path.dirname(__file__))
    filepath = os.path.join(dirname, "resources/csvdata/Berlin/Rides/VM2_493290084")
    settings.logging.info(f"Testing the module with {filepath}")

    with DatabaseConnection() as cur:
        handle_ride_file(filepath, cur)
