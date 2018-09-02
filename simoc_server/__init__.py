import os
import sys

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

sys.path.insert(0, os.path.join("mesa"))

if os.path.isfile("settings.py"):
    config_obj = os.environ.get("DIAG_CONFIG_MODULE", "settings")
else:
    config_obj = os.environ.get("DIAG_CONFIG_MODULE", "simoc_server.default_settings")

app = Flask(__name__)

app.config.from_object(config_obj)

db_type = os.environ.get("DB_TYPE")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_dns = os.environ.get("DB_DNS_NAME")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

if db_type == 'mysql':
    SQLALCHEMY_DATABASE_URI = (
        'mysql+mysqldb://{user}:{password}@{dns}:{port}/{database}').format(
            user=db_user, password=db_password,
            dns = db_dns, port=db_port,
            database=db_name)
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app, session_options={
    "expire_on_commit": False
    })

import simoc_server.views