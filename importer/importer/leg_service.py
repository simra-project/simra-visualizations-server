import pandas as pd
import random

POSTGIS_SURROUNDING_RIDE_BUFFER_SIZE = 0.0001


def determine_legs(map_matched_coords, cur):
    insert_map_matched_coords(map_matched_coords, cur)
    return find_legs(cur)


def insert_map_matched_coords(map_matched_coords, cur):
    cur.execute('DROP TABLE IF EXISTS ride;')
    cur.execute('CREATE TEMP TABLE ride (geometry geometry NOT NULL);')

    insert_map_matched_query = 'INSERT INTO ride VALUES (st_buffer(st_makeline(ARRAY['

    for coord in map_matched_coords:
        insert_map_matched_query += 'St_SetSRID(st_makepoint(' + str(coord[0]) + ',' + str(coord[1]) + '), 4326),'
    if len(map_matched_coords) > 0:
        insert_map_matched_query = insert_map_matched_query[:-1]
    insert_map_matched_query += ']::geometry[]), ' + str(POSTGIS_SURROUNDING_RIDE_BUFFER_SIZE) + '));'
    cur.execute(insert_map_matched_query)


def find_legs(cur):
    query = '''
        SELECT 
           sub.id,
           sub."osmId",
           st_astext(st_transform(sub.geomerty_rounded, 4326)),
           "streetName",
           count,
           score,
           "weekdayCount",
           "rushhourCount"
        FROM (
             SELECT
                    l.id,
                    l."osmId",
                    st_transform(l.geom, 4326) as geomerty_rounded,
                    "streetName",
                    count,
                    score,
                    "weekdayCount",
                    "rushhourCount"
             FROM ride r,
                  public."SimRaAPI_osmwayslegs" l
             WHERE r.geometry && l.geom
             LIMIT 100000) AS sub, ride r
        WHERE st_intersects(r.geometry, st_startpoint(sub.geomerty_rounded))
          AND st_intersects(st_endpoint(sub.geomerty_rounded), r.geometry);
    '''
    cur.execute(query)
    return cur.fetchall()


def update_legs(ride, legs, cur):
    df = pd.DataFrame(data=legs, index=range(len(legs)),
                      columns=['id', 'osm_id', 'geometry', 'street_name', 'count', 'score', 'weekday_count',
                               'rushhour_count'])
    df['count'] += 1
    for i, leg in df.iterrows():
        # todo calc road score here
        df.at[i, 'score'] = random.uniform(0, 1)
        if is_weekday(ride.timestamps):
            df.at[i, 'weekday_count'] += 1
        if is_rushhour(ride.timestamps):
            df.at[i, 'rushhour_count'] += 1

    tuples = [tuple(x) for x in df[['count', 'score', 'weekday_count', 'rushhour_count', 'id']].to_numpy()]

    cur.execute("""
        CREATE TEMP TABLE updated_legs(count INT, score FLOAT, weekday_count INT, rushhour_count INT, id BIGINT) ON COMMIT DROP
        """)

    cur.executemany("""
      INSERT INTO updated_legs (count, score, weekday_count, rushhour_count, id)
      VALUES(%s, %s, %s, %s, %s)""",
                    tuples)
    cur.execute("""
            UPDATE public."SimRaAPI_osmwayslegs"
            SET 
                count = updated_legs.count,
                score = updated_legs.score,
                "weekdayCount" = updated_legs.weekday_count,
                "rushhourCount" = updated_legs.rushhour_count
            FROM updated_legs
            WHERE updated_legs.id = public."SimRaAPI_osmwayslegs".id;
            """)


def is_weekday(timestamps):
    return timestamps[0].weekday() < 5


def is_rushhour(timestamps):
    hour = timestamps[0].hour
    return (7 <= hour <= 14) | (15 <= hour <= 18)
