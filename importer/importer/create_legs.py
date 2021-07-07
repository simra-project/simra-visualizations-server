from settings import logging
from db_connection import DatabaseConnection

"""A python module to populate the simra database with leg entities."""

if __name__ == "__main__":
    with DatabaseConnection() as cur:
        logging.info("Inserting data into the table 'OsmWaysJunctions'")
        cur.execute(
            """
            INSERT INTO public."SimRaAPI_osmwaysjunctions" (point)
            SELECT ST_Transform((ST_DumpPoints(geometry)).geom, 4326) AS point
            FROM import.osm_ways
            GROUP BY point
            HAVING count(*) >= 2
            """
        )
        logging.info("... Success")

        logging.info("Inserting data into the table 'OsmWaysLegs'")
        cur.execute(
            """
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER count SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER score SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "weekdayCount" SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "morningCount" SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "eveningCount" SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "normalIncidentCount" SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "scaryIncidentCount" SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "score_array" SET DEFAULT array[]::float[];
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "velocity" SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "velocity_array" SET DEFAULT array[]::float[];
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "avoidedCount" SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmwayslegs" ALTER "chosenCount" SET DEFAULT 0;
            """
        )
        cur.execute(
            """
            INSERT INTO public."SimRaAPI_osmwayslegs" ("osmId", "geom", "streetName", "postalCode", "highwayName")
            SELECT osm_id,
                (ST_Dump(ST_Split(
                    ST_Transform(geometry, 4326),
                    ST_Collect(public."SimRaAPI_osmwaysjunctions".point))
                )).geom AS geometry,
                street_name,
                postal_code,
                highway_type
            FROM import.osm_ways
            JOIN public."SimRaAPI_osmwaysjunctions" ON
            public."SimRaAPI_osmwaysjunctions".point && ST_Transform(import.osm_ways.geometry, 4326)
            GROUP BY osm_id,
            geometry,
            street_name,
            postal_code,
            highway_type;
            """
        )
        logging.info("... Success")

        logging.info("Inserting data into the table 'OsmLargeJunctions'")
        cur.execute(
            """
            ALTER TABLE public."SimRaAPI_osmlargejunctions" ALTER count SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmlargejunctions" ALTER "totalDuration" SET DEFAULT 0;
            ALTER TABLE public."SimRaAPI_osmlargejunctions" ALTER "avgDuration" SET DEFAULT 0;
            """
        )
        cur.execute(
            """
            INSERT INTO public."SimRaAPI_osmlargejunctions" (point)
            SELECT st_transform((ST_DumpPoints(geom)).geom, 4326) AS point
            FROM public."SimRaAPI_osmwayslegs"
            WHERE "highwayName" = 'primary'
                OR "highwayName" = 'secondary'
                OR "highwayName" = 'secondary_link'
                OR "highwayName" = 'tertiary'
                OR "highwayName" = 'tertiary_link'
                OR "highwayName" = 'living_street'
                OR "highwayName" = 'residential'
                OR "highwayName" = 'cycleway'
            GROUP BY point
            HAVING count(*) >= 3
            """
        )
        logging.info("... Success")
