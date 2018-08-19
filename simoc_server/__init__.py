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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@127.0.0.1/simoc'.format(db_user, db_password)

db = SQLAlchemy(app, session_options={
    "expire_on_commit": False
    })

import simoc_server.views