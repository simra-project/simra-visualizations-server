from settings import *
from db_connection import DatabaseConnection

if __name__ == '__main__':
    with DatabaseConnection() as cur:
        print("[*] Creating geojson dump")
        cur.execute("""
SELECT jsonb_build_object(
    'type', 'Feature',
    'geometry', ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(row) - 'geom'
) FROM (SELECT * FROM public."SimRaAPI_osmwayslegs") row;
        """)
        final_geojson = """
"type": "FeatureCollection",
"features": [
"""
        final_geojson += "\n".join(map(lambda x: str(x[0]), cur.fetchall()))
        final_geojson += "\n]"
        with open("simra_legs.geojson", "w") as f:
            f.write(final_geojson)
        print("[+] done, saved in simra_legs.geojson")
