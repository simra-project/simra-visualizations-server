from geopy.distance import great_circle
from importer.importer.settings import COVERED_DISTANCE_INSIDE_STOP_THRESHOLD, DISTANCE_TO_JUNCTION_THRESHOLD


def find_junctions(legs, cur):
    legs_ids = [(leg[0],) for leg in legs]
    cur.execute("""
            CREATE TEMP TABLE tmp_legs(leg_id BIGINT) ON COMMIT DROP
            """)

    cur.executemany("""
          INSERT INTO tmp_legs
          VALUES(%s)""",
                    legs_ids)
    cur.execute("""
                SELECT DISTINCT j.id, j.count, j."totalDuration"
                FROM (  SELECT l.geom
                        FROM tmp_legs as t
                        JOIN "SimRaAPI_osmwayslegs" l on t.leg_id = l.id
                ) as sub,
                "SimRaAPI_osmlargejunctions" j
                WHERE st_intersects(sub.geom,j.point)
                """)
    return cur.fetchall()


def process_stops(ride, legs, cur):
    all_ride_junctions = find_junctions(legs, cur)
    raw_stops = find_stops_in_raw_coords(ride)
    stops = find_junctions_of_stops(raw_stops, cur)
    no_stop_junctions = [jnc for jnc in all_ride_junctions if jnc[0] not in [stop.junction[0] for stop in stops]]  # junctions, where cyclist did not stop
    for jnc in no_stop_junctions:
        update_junction(jnc, 0, cur)
    for stop in stops:
        if stop.junction is None:
            continue
        update_junction(stop.junction, stop.duration.seconds, cur)

def find_stops_in_raw_coords(ride):
    stops = []
    coords = ride.raw_coords
    inside_stop = False
    for i, coord in enumerate(coords):
        if i + 1 < len(coords):
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


def find_junctions_of_stops(stops, cur):
    for stop in stops:
        junction = match_junction_to_stop(stop, cur)
        if junction[3] > DISTANCE_TO_JUNCTION_THRESHOLD:  # stop is ignored as cyclist did not stop at a junction but somewhere on the way
            continue
        stop.junction = junction
    stops = [stop for stop in stops if stop.junction is not None]
    return stops


def match_junction_to_stop(stop, cur):
    query = """    
        SELECT 
            j.id,
            j.count,
            j."totalDuration",
            ST_Distance(
                   j.point,
                   st_setsrid(st_makepoint({0}, {1}), 4326)
               ) * 111000 AS distance_in_meters
        FROM public."SimRaAPI_osmlargejunctions" j
        ORDER BY point <->
            st_setsrid(st_makepoint({0}, {1}), 4326)
        LIMIT 1;
        """.format(stop.raw_coord[0], stop.raw_coord[1])
    cur.execute(query)
    return cur.fetchone()


def update_junction(junction, new_duration, cur):
    count = junction[1] + 1
    cum_duration = junction[2] + new_duration
    avg_duration = cum_duration / count
    query = """
            UPDATE public."SimRaAPI_osmlargejunctions"
            SET 
                count = {0},
                "totalDuration" = {1}, 
                "avgDuration" = {2}
            WHERE id = {3};
    """.format(count, cum_duration, avg_duration, junction[0])
    cur.execute(query)


class Stop:
    def __init__(self, raw_coord):
        self.raw_coord = raw_coord
        self.junction = None
        self.duration = None
