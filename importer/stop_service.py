from geopy.distance import great_circle
from importer.settings import COVERED_DISTANCE_INSIDE_STOP_THRESHOLD, DISTANCE_TO_JUNCTION_THRESHOLD


def process_stops(ride, cur):
    raw_stops = find_stops_in_raw_coords(ride)
    update_junctions_of_stops(raw_stops, cur)


def find_stops_in_raw_coords(ride):
    stops = []
    coords = ride.raw_coords
    inside_stop = False
    for i, coord in enumerate(coords):
        if i + 1 < len(coords):
            dist = great_circle(coords[i], coords[i + 1]).meters
            if great_circle(coords[i], coords[i + 1]).meters < COVERED_DISTANCE_INSIDE_STOP_THRESHOLD:
                if not inside_stop:
                    inside_stop = True
                    stop = Stop(coord)
                    start = ride.timestamps[i]
            else:
                if inside_stop:
                    stop.duration = ride.timestamps[i] - start
                    stops.append(stop)
                    inside_stop = False
        else:
            break
    return stops


def update_junctions_of_stops(stops, cur):
    for stop in stops:
        junction = match_junction_to_stop(stop, cur)
        if junction[3] > DISTANCE_TO_JUNCTION_THRESHOLD:  # stop is ignored as cyclist did not stop at a junction but somewhere on the way
            continue
        stop.junction_id = junction[0]
        update_junction(junction, stop, cur)


def match_junction_to_stop(stop, cur):
    query = """    
        SELECT 
            j.id,
            j.count,
            j.cum_duration,
            ST_Distance(
                   j.point,
                   st_setsrid(st_makepoint({0}, {1}), 4326)
               ) * 111000 AS distance_in_meters
        FROM osm_large_junctions j
        ORDER BY point <->
            st_setsrid(st_makepoint({0}, {1}), 4326)
        LIMIT 1;
        """.format(stop.raw_coord[0], stop.raw_coord[1])
    cur.execute(query)
    return cur.fetchone()


def update_junction(junction, stop, cur):
    count = junction[1] + 1
    cum_duration = junction[2] + stop.duration.seconds
    query = """
            UPDATE osm_large_junctions
            SET 
                count = {0},
                cum_duration = {1}
            WHERE id = {2};
    """.format(count, cum_duration, junction[0])
    cur.execute(query)


class Stop:
    def __init__(self, raw_coord):
        self.raw_coord = raw_coord
        self.junction_id = None
        self.duration = None
