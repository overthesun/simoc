from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

config_obj = os.environ.get("DIAG_CONFIG_MODULE", "simoc_server.default_settings")

app = Flask(__name__)

app.config.from_object(config_obj)
db = SQLAlchemy(app, session_options={
    "expire_on_commit": False
    })

import simoc_server.views