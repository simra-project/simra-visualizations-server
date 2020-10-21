import csv

from datetime import date
from postgis import Point


def handle_incidents(data, filename, cur):
    data = csv.DictReader(data[1:], delimiter=",")
    filename = filename.split("/")[-1]
    pLoc = -1
    for row in data:
        rideTimestamp = date.fromtimestamp(int(row.get("ts", 0)) / 1000)
        bikeType = row.get("bike", -1)
        childCheckbox = row.get("childCheckBox", 0) == "1"
        trailerCheckbox = row.get("trailerCheckBox", 0) == "1"
        pLoc = row.get("pLoc", -1)
        incident = row.get("incident", -1)
        if not incident:
            incident = -1
        iType = -1
        i = 1
        while f"i{i}" in row:
            if row[f"i{i}"] == "1":
                iType = i
                break
            i += 1
        scary = row.get("scary", 0) == "1"
        desc = row.get("desc", "")
        geom = Point(row["lon"], row["lat"], srid=4326)

        cur.execute("""
            INSERT INTO public."SimRaAPI_incident" ("rideTimestamp", "bikeType", "childCheckbox", "trailerCheckbox", "pLoc", "incident", "iType", "scary", "desc", "filename", "geom") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [rideTimestamp, bikeType, childCheckbox, trailerCheckbox, pLoc, incident, iType, scary, desc, filename, geom])
    return int(pLoc)
