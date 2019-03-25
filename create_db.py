import argparse
import os

import simoc_server
from simoc_server import app
from simoc_server.database import *
from simoc_server.database.seed_data import seed_agents


def confirm(message):
    choice = input(message + "[y/N]")
    if choice.lower() != "y":
        return False
    return True


def create(agent_conf):
    db.create_all()
    seed_agents.seed(agent_conf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database")
    parser.add_argument("--no_seed", action="store_true",
                        help="Do not add seed data.")
    args = parser.parse_args()

    if app.config['DB_TYPE'] == 'sqlite':
        db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
        sqlite_uri_start = "sqlite:///"
        if db_uri.startswith(sqlite_uri_start):
            if db_uri.startswith(sqlite_uri_start + "/"):
                db_path = db_uri[len(sqlite_uri_start):]
            else:
                db_rel_path = db_uri[len(sqlite_uri_start):]
                package_path = os.path.dirname(simoc_server.__file__)
                db_path = os.path.join(package_path, db_rel_path)
            if os.path.isfile(db_path):
                #if not confirm("Database already exists, continuing will delete old database"):
                #    print("Exiting without creating database")
                #    exit()
                #else:
                os.remove(db_path)
        else:
            #if not confirm("Continuing will delete old database"):
            #    print("Exiting without creating database")
            #    exit()
            #else:
            db.sessionmaker.close_all()
            # db.engine.dispose()
            db.drop_all()

    create(app.config["AGENT_CONFIG"])

    os._exit(0)