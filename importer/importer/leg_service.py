"""Service which manipulates the osmwayslegs database table.

Methods
-------
    determine_legs(map_matched_coords, cur)
        Determines the legs of the OSM service, belonging to a specific
        ride.
    insert_map_matched_coords(map_matched_coords, cur)
        Saves the map matched coordinates as an entity into a temporary
        database 'ride'.
    find_legs(cur)
        Retrieves all OSM legs which are part of a certain ride.
    update_legs
        Calculates measures for legs belonging to a specific ride and
        save the new information into the database.
    update_avoided_legs
        Updates the 'avoidedCount' attribute in the database of all
        given legs of the set.
    is_weekday : bool
    is_morning : bool
    is_evening : bool
"""

import pandas as pd
from postgis.linestring import LineString
from settings import logging

POSTGIS_SURROUNDING_RIDE_BUFFER_SIZE = 0.00002


def determine_legs(map_matched_coords, cur):
    """Determines the legs of the OSM service, belonging to a specific
    ride.

    Returns
    -------
    List of legs
        Legs, belonging to the map matched coordinates of the ride,
        passed as a parameter.
    """
    insert_map_matched_coords(map_matched_coords, cur)
    return find_legs(cur)


def insert_map_matched_coords(map_matched_coords, cur):
    """Saves the map matched coordinates as an entity into a temporary
    database 'ride'.

    Parameters
    ----------
    map_matched_coords
        List of coordinates, map matched by the graphhopper service.
    cur : DatabaseConnection
    """

    cur.execute("DROP TABLE IF EXISTS ride;")
    cur.execute("CREATE TEMP TABLE ride (geometry geometry NOT NULL);")

    insert_map_matched_query = "INSERT INTO ride VALUES (st_buffer(st_makeline(ARRAY["

    for coord in map_matched_coords:
        insert_map_matched_query += (
            "St_SetSRID(st_makepoint("
            + str(coord[0])
            + ","
            + str(coord[1])
            + "), 4326),"
        )
    if len(map_matched_coords) > 0:
        insert_map_matched_query = insert_map_matched_query[:-1]
    insert_map_matched_query += (
        "]::geometry[]), " + str(POSTGIS_SURROUNDING_RIDE_BUFFER_SIZE) + "));"
    )
    cur.execute(insert_map_matched_query)


def find_legs(cur):
    """Retrieves all OSM legs which are part of a certain ride. The
    ride has to be temporarily saved in the database table 'ride' which
    is created by callling the function insert_map_matched_coords().

    Parameters
    ----------
    cur : DatabaseConnection
    """
    query = """
        SELECT 
           sub.id,
           sub."osmId",
           st_astext(st_transform(sub.geom, 4326)),
           "streetName",
           count,
           score,
           "weekdayCount",
           "morningCount",
           "eveningCount",
           "score_array",
           "velocity",
           "velocity_array",
           "normalIncidentCount",
           "scaryIncidentCount",
           "avoidedCount",
           "chosenCount"
        FROM (
             SELECT
                    l.id,
                    l."osmId",
                    st_transform(l.geom, 4326) as geom,
                    "streetName",
                    count,
                    score,
                    "weekdayCount",
                    "morningCount",
                    "eveningCount",
                    "score_array",
                    "velocity",
                    "velocity_array",
                    "normalIncidentCount",
                    "scaryIncidentCount",
                    "avoidedCount",
                    "chosenCount"
             FROM ride r,
                  public."SimRaAPI_osmwayslegs" l
             WHERE r.geometry && l.geom
             LIMIT 100000) AS sub, ride r
        WHERE st_contains(r.geometry, sub.geom);
        """
    cur.execute(query)
    return cur.fetchall()


def update_legs(
    ride,
    legs,
    shortest_path_legs,
    cur,
    IRI,
    phone_loc,
    velocity_sections,
    incident_locs,
    is_detour,
):
    """Calculates measures for legs belonging to a specific ride and
    save the new information into the database.

    Parameters
    ----------
    legs
        List of OSM legs with all their attributes which where
        traversed by the cyclist.
    shortest_path_legs
        Set of legs which are part of the shortest route of the
        trajectory.
    phone_loc
        The location of the phone during the ride.
    is_detour : bool
        Whether the trajectory should be counted as a detour because
        it exceeds the threshold parameters.
    """
    # Current state of the OSM service legs
    df = pd.DataFrame(
        data=legs,
        index=range(len(legs)),
        columns=[
            "id",
            "osm_id",
            "geometry",
            "street_name",
            "count",
            "score",
            "weekday_count",
            "morning_count",
            "evening_count",
            "score_array",
            "velocity",
            "velocity_array",
            "normal_incident_count",
            "scary_incident_count",
            "avoided_count",
            "chosen_count",
        ],
    )

    # Increase counters
    df["count"] += 1
    for i, leg in df.iterrows():
        # TODO: Put if outside of for loop
        if is_weekday(ride.timestamps):
            df.at[i, "weekday_count"] += 1
        if is_morning(ride.timestamps):
            df.at[i, "morning_count"] += 1
        if is_evening(ride.timestamps):
            df.at[i, "evening_count"] += 1

    # Increase avoided and chosen counters, if trajectory was a detour.
    if is_detour:
        # All legs which where not traversed and which are part of the
        # shortest trajectory.
        avoided = list(
            filter(
                lambda shortest_path_sleg: True
                if shortest_path_sleg not in legs
                else False,
                shortest_path_legs,
            )
        )
        update_avoided_legs(avoided, cur)

        # All legs which where travered but which are not part of the
        # shortest trajectory.
        chosen = list(
            filter(lambda sleg: True if sleg not in shortest_path_legs else False, legs)
        )
        for idx, leg in enumerate(legs):
            if leg in chosen:
                df.at[idx, "chosen_count"] += 1

    # Create a temporary table to buffer updated leg information
    cur.execute(
        """
        CREATE TEMP TABLE updated_legs(
            count INT,
            score FLOAT,
            weekday_count INT,
            morning_count INT,
            evening_count INT,
            id BIGINT,
            score_array FLOAT[],
            velocity FLOAT,
            velocity_array FLOAT[],
            normal_incident_count INT,
            scary_incident_count INT,
            avoided_count INT,
            chosen_count INT
        )
        ON COMMIT DROP
        """
    )

    # Create a temporary database table for the legs of the ride which
    # need to be matched.
    cur.execute(
        """
        CREATE TEMP TABLE legs_to_match(id BIGINT, geom GEOMETRY(LINESTRING,4326)) ON COMMIT DROP
        """
    )
    tup = [tuple(x) for x in df[["id", "geometry"]].to_numpy()]
    cur.executemany(
        """
        INSERT INTO legs_to_match (id, geom) VALUES(%s, ST_GeomFromText(%s,4326))
        """,
        tup,
    )

    # If the phones was attached to the bikes handelbar, calculate a
    # street quality score.
    if phone_loc == 1 or phone_loc == "1":  # Handlebar
        from tqdm import tqdm

        for iri in tqdm(IRI):
            cur.execute(
                """
                SELECT
                    id,
                    ST_Distance(
                        geom, ST_SetSRID(ST_MakePoint(%s, %s),4326)
                    ) as d
                FROM legs_to_match ORDER BY d ASC LIMIT 1
                """,
                (iri[2][0], iri[2][1]),
            )
            candidates = cur.fetchall()
            for candidate in candidates:
                if candidate[0] in list(df["id"]):
                    for i in df.loc[df["id"] == candidate[0]]["score_array"]:
                        i.append(iri[0])
                    break

        for i, leg in df.iterrows():
            if len(df.at[i, "score_array"]) > 0:
                df.at[i, "score"] = sum(df.at[i, "score_array"]) / len(
                    df.at[i, "score_array"]
                )
            else:
                df.at[i, "score"] = -1

    # Process near miss incidents
    for incident in incident_locs:
        cur.execute(
            """
            SELECT id, ST_Distance(geom, %s) as d
            FROM legs_to_match ORDER BY d ASC LIMIT 1
            """,
            (incident[0],),
        )
        candidates = cur.fetchall()
        for candidate in candidates:
            if candidate[0] in list(df["id"]):
                if not incident[1]:
                    df.loc[df["id"] == candidate[0], "normal_incident_count"] += 1
                else:
                    df.loc[df["id"] == candidate[0], "scary_incident_count"] += 1

    # Process velocity data
    for vel_section in velocity_sections:
        cur.execute(
            """
            SELECT
                id,
                ST_Distance(
                    geom, ST_SetSRID(ST_MakePoint(%s, %s),4326)
                ) as d
            FROM legs_to_match ORDER BY d ASC LIMIT 1
            """,
            (vel_section[0][0][0], vel_section[0][0][1]),
        )
        candidates = cur.fetchall()
        for candidate in candidates:
            if candidate[0] in list(df["id"]):
                for i in df.loc[df["id"] == candidate[0]]["velocity_array"]:
                    i.append(vel_section[2])
                break

    for i, leg in df.iterrows():
        if len(df.at[i, "velocity_array"]) > 0:
            df.at[i, "velocity"] = sum(df.at[i, "velocity_array"]) / len(
                df.at[i, "velocity_array"]
            )
        else:
            df.at[i, "velocity"] = -1

    # Store updated information in the temporary database table
    # 'updated_legs'.
    tuples = [
        tuple(x)
        for x in df[
            [
                "count",
                "score",
                "weekday_count",
                "morning_count",
                "evening_count",
                "id",
                "score_array",
                "velocity",
                "velocity_array",
                "normal_incident_count",
                "scary_incident_count",
                "avoided_count",
                "chosen_count",
            ]
        ].to_numpy()
    ]
    cur.executemany(
        """
        INSERT INTO updated_legs (
            count,
            score,
            weekday_count,
            morning_count,
            evening_count,
            id,
            score_array,
            velocity,
            velocity_array,
            normal_incident_count,
            scary_incident_count,
            avoided_count,
            chosen_count
        )
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        tuples,
    )

    # Move updated leg data into the persistend database table
    # 'SimRaAPI_osmwayslegs'.
    cur.execute(
        """
        UPDATE public."SimRaAPI_osmwayslegs"
        SET 
            count = updated_legs.count,
            score = updated_legs.score,
            "weekdayCount" = updated_legs.weekday_count,
            "morningCount" = updated_legs.morning_count,
            "eveningCount" = updated_legs.evening_count,
            "score_array" = updated_legs.score_array,
            "velocity" = updated_legs.velocity,
            "velocity_array" = updated_legs.velocity_array,
            "normalIncidentCount" = updated_legs.normal_incident_count,
            "scaryIncidentCount" = updated_legs.scary_incident_count,
            "avoidedCount" = updated_legs.avoided_count,
            "chosenCount" = updated_legs.chosen_count
        FROM updated_legs
        WHERE updated_legs.id = public."SimRaAPI_osmwayslegs".id;
        """
    )


def update_avoided_legs(avoided_legs, cur):
    """Updates the 'avoidedCount' attribute in the database of all
    given legs of the set.

    Parameters
    ----------
    avoided_legs
        List of legs which where circumnavigated by the cyclist.
    cur : DatabaseConnection
    """

    for leg in avoided_legs:
        leg_avoided_count = leg[14] + 1
        leg_id = leg[0]

        cur.execute(
            """
            UPDATE public."SimRaAPI_osmwayslegs"
            SET "avoidedCount" = %s
            WHERE public."SimRaAPI_osmwayslegs".id = %s;
            """,
            (leg_avoided_count, leg_id),
        )


def is_weekday(timestamps):
    return timestamps[0].weekday() < 5


def is_morning(timestamps):
    hour = timestamps[int(len(timestamps) / 2)].hour
    return 6 <= hour < 9


def is_evening(timestamps):
    hour = timestamps[int(len(timestamps) / 2)].hour
    return 16 <= hour < 19
