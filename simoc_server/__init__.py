import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, os.path.join("mesa"))

if os.path.isfile("settings.py"):
    config_obj = os.environ.get("DIAG_CONFIG_MODULE", "settings")
else:
    config_obj = os.environ.get(
        "DIAG_CONFIG_MODULE", "simoc_server.default_settings")

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")

app.config.from_object(config_obj)

agent_config = os.environ.get("AGENT_CONFIG", 'agent_desc.json')
app.config['AGENT_CONFIG'] = agent_config

db_name = os.environ.get("DB_NAME")
db_type = os.environ.get("DB_TYPE")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_dns = os.environ.get("DB_DNS_NAME")
db_port = os.environ.get("DB_PORT")

if db_type == 'mysql':
    SQLALCHEMY_DATABASE_URI = (
        'mysql+mysqldb://{user}:{password}@{dns}:{port}/{database}').format(
        user=db_user, password=db_password,
        dns=db_dns, port=db_port,
        database=db_name)
elif db_type == 'postgres':
    SQLALCHEMY_DATABASE_URI = (
        'postgres://{user}:{password}@{dns}:{port}/{database}').format(
        user=db_user, password=db_password,
        dns=db_dns, port=db_port,
        database=db_name)
elif db_type == 'sqlite':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
else:
    print('Unknown DB_TYPE variable: "{}"'.format(db_type))
    print('Using SQLite by default')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    db_type = 'sqlite'

app.config['DB_TYPE'] = db_type
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app, session_options={
    "expire_on_commit": False
})

import simoc_server.views
import simoc_server.front_end_routes
