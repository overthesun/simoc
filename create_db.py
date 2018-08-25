import argparse
import os
import simoc_server
from simoc_server import db, app
from simoc_server.database import *
from simoc_server.database.seed_data import seed

import sqlalchemy as sa

def confirm(message):
    choice = input(message + "[y/N]")
    if choice.lower() != "y":
        return False
    return True

def create(seed_data):
    db.create_all()
    if(seed_data):
        seed.seed()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database")
    parser.add_argument("--no_seed", action="store_true", help="Do not add seed data.")
    args = parser.parse_args()

    # db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    # sqlite_uri_start = "sqlite:///"
    # if db_uri.startswith(sqlite_uri_start):
    #     if db_uri.startswith(sqlite_uri_start + "/"):
    #         db_path = db_uri[len(sqlite_uri_start):]
    #     else:
    #         db_rel_path = db_uri[len(sqlite_uri_start):]
    #         package_path = os.path.dirname(simoc_server.__file__)
    #         db_path = os.path.join(package_path, db_rel_path)
    #     if os.path.isfile(db_path):
    #         if not confirm("Database already exists, continuing will delete old database"):
    #             print("Exiting without creating database")
    #             exit()
    #         else:
    #             os.remove(db_path)
    # else:
    #     if not confirm("Continuing will delete old database"):
    #             print("Exiting without creating database")
    #             exit()
    #     else:
    #         db.sessionmaker.close_all()
    #         # db.engine.dispose()
    #         db.drop_all()
    #     db.sessionmaker.close_all()
    #     # db.engine.dispose()
    #     db.drop_all()

    # create(seed_data=(not args.no_seed))

    db.sessionmaker.close_all()
    create(seed_data=(not args.no_seed))

    # temporary fix for poorly handled threading
    os._exit(0)