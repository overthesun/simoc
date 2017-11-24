from flask_sqlalchemy import SQLAlchemy
from flask import Flask
app = Flask(__name__)
db = SQLAlchemy(app)

app.config.from_object("simoc_server.default_settings")

import simoc_server.views