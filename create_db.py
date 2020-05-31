import argparse
import os
import time

os.environ["NO_FLASK"] = "1"

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

    num_retries = 10
    interval = 5
    while True:
        try:
            app.logger.info(f"Populating the '{app.config['DB_TYPE']}' database at '{app.config['SQLALCHEMY_DATABASE_URI']}' with '{app.config['AGENT_CONFIG']}' config file.")
            create(app.config["AGENT_CONFIG"])
            break
        except Exception as e:
            app.logger.info(e)
            if num_retries > 0:
                num_retries -= 1
                app.logger.info(f"Unable to populate '{app.config['DB_TYPE']}' database. Retrying in {interval} seconds.")
                time.sleep(interval)
                continue
            else:
                raise Exception("Error while populating the database.")

    app.logger.info(f"The '{app.config['DB_TYPE']}' database was successfully populated.")

