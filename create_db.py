import argparse
import os
import time

os.environ["NO_FLASK"] = "1"

from simoc_server import app
from simoc_server.database import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database")
    parser.add_argument("--no_seed", action="store_true",
                        help="Do not add seed data.")
    args = parser.parse_args()

    num_retries = 10
    interval = 5
    while True:
        try:
            app.logger.info(f"Populating the '{app.config['DB_TYPE']}' database at '{app.config['SQLALCHEMY_DATABASE_URI']}'.")
            db.create_all()  # Adds the User table to database
            break
        except Exception as e:
            # TODO: catch sqlalchemy.exc.DatabaseError: (mysql.connector.errors.DatabaseError)
            #    2003 (HY000): Can't connect to MySQL server on 'simoc-db' (111)
            # specifically instead of all errors.
            #print('*** Error:', e)
            app.logger.info(e)
            if num_retries > 0:
                num_retries -= 1
                app.logger.info(f"Unable to populate '{app.config['DB_TYPE']}' database. Retrying in {interval} seconds.")
                time.sleep(interval)
                continue
            else:
                raise Exception("Error while populating the database.")

    app.logger.info(f"The '{app.config['DB_TYPE']}' database was successfully populated.")

