import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis


if os.path.isfile("settings.py"):
    config_obj = os.environ.get("DIAG_CONFIG_MODULE", "settings")
else:
    config_obj = os.environ.get(
        "DIAG_CONFIG_MODULE", "simoc_server.default_settings")

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")

app.config.from_object(config_obj)

agent_config = os.environ.get("AGENT_CONFIG", 'agent_desc.json')
app.config['AGENT_CONFIG'] = agent_config

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False

no_flask = os.environ.get("NO_FLASK")

redis_host = os.environ.get("REDIS_HOST", 'localhost')
redis_port = os.environ.get("REDIS_PORT", '6379')
redis_password = os.environ.get("REDIS_PASSWORD", '')

redis_conn = redis.StrictRedis(host=redis_host, port=int(redis_port), password=redis_password)

db_type = os.environ.get("DB_TYPE")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")

if db_type == 'mysql':
    database_url = f'mysql+mysqldb://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
elif db_type == 'postgres':
    database_url = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
elif db_type == 'sqlite':
    database_url = 'sqlite:///../sqlite/db.sqlite'
else:
    print('Unknown DB_TYPE variable: "{}"'.format(db_type))
    print('Using SQLite by default')
    database_url = 'sqlite:///../sqlite/db.sqlite'
    db_type = 'sqlite'

if db_type == 'sqlite':
    sqlite_dir = './sqlite'
    if not os.path.exists(sqlite_dir):
        try:
            os.makedirs(sqlite_dir)
        except FileExistsError:
            pass

app.config['DB_TYPE'] = db_type
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

db = SQLAlchemy(app, session_options={
    "expire_on_commit": False
})

if no_flask and int(no_flask) == 1:
    pass
else:
    import simoc_server.views
    import simoc_server.front_end_routes
