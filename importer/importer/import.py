from settings import *
import os
from db_connection import DatabaseConnection
import datetime
import tqdm

import profile, rides

if __name__ == "__main__":
    files = []
    for r, d, f in os.walk(IMPORT_DIRECTORY, followlinks=True):
        for file in f:
            if "." not in file:
                files.append(os.path.join(r, file))
    for file in tqdm.tqdm(files):
        if "Profiles" in file:  # Don't process further, when not a ride file.
            continue
        filename = file.split("/")[-1]
        region = file.split("/")[-3]
        with DatabaseConnection() as cur:
            cur.execute(
                """
                SELECT * FROM public."SimRaAPI_parsedfiles" WHERE "fileName" LIKE %s
                """,
                (f"%{filename}%",),
            )
            if (
                cur.fetchone() is not None
            ):  # Don't process further, if ride already exists.
                continue
        try:
            with DatabaseConnection() as cur:  # new database connection for the whole transaction
                if "Profiles" in file:
                    profile.handle_profile(file, cur)
                    continue
                else:
                    logging.info(file)
                    rides.handle_ride_file(file, cur)

                cur.execute(
                    """
                    INSERT INTO public."SimRaAPI_parsedfiles" ("fileName", "fileType", "region", "importTimestamp") VALUES (%s, %s, %s, %s)
                    """,
                    [
                        filename,
                        "profile" if "Profiles" in file else "ride",
                        region,
                        datetime.datetime.utcnow(),
                    ],
                )
        except Exception as e:
            logging.exception(f"Skipped ride {filename} due to exception {e}")
            raise (e)
