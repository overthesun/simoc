import os
import sys

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

sys.path.insert(0, os.path.join("mesa"))

if os.path.isfile("settings.py"):
    config_obj = os.environ.get("DIAG_CONFIG_MODULE", "settings")
else:
    config_obj = os.environ.get("DIAG_CONFIG_MODULE", "simoc_server.default_settings")

print(__name__)
app = Flask(__name__)

app.config.from_object(config_obj)

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")

CLOUDSQL_DB_NAME = 'simoc'
GAE_PROJECT_ID = 'simoc-213717'
CLOUDSQL_CONNECTION_NAME = 'simoc-213717:us-central1:simoce'

SQLALCHEMY_DATABASE_URI = (
    'mysql+mysqldb://{user}:{password}@localhost/{database}'
    '?unix_socket=/cloudsql/{connection_name}').format(
        user=db_user, password=db_password,
        database=CLOUDSQL_DB_NAME, connection_name=CLOUDSQL_CONNECTION_NAME)
print(SQLALCHEMY_DATABASE_URI)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@127.0.0.1/proxyuser'.format(db_user, db_password)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app, session_options={
    "expire_on_commit": False
    })

import simoc_server.views