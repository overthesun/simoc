import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis

from simoc_server.exceptions import ServerError


if os.path.isfile('settings.py'):
    config_obj = os.environ.get('DIAG_CONFIG_MODULE', 'settings')
else:
    config_obj = os.environ.get('DIAG_CONFIG_MODULE', 'simoc_server.default_settings')

app = Flask(__name__, static_folder='./dist/static', template_folder='./dist')

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 't00p__s3cr3t!?')

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

app.config.from_object(config_obj)

app.config['AGENT_CONFIG'] = os.environ.get('AGENT_CONFIG', 'agent_desc.json')

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', '6379')
redis_password = os.environ.get('REDIS_PASSWORD', None)

if not redis_password:
    redis_url = f'redis://{redis_host}:{redis_port}'
else:
    redis_url = f'redis://:{redis_password}@{redis_host}:{redis_port}'

redis_conn = redis.Redis.from_url(redis_url,
                                  health_check_interval=30,
                                  socket_keepalive=True,
                                  retry_on_timeout=True,
                                  socket_timeout=300,
                                  socket_connect_timeout=30)

db_type = os.environ.get('DB_TYPE')
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')

if db_type == 'mysql':
    database_url = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
elif db_type == 'postgres':
    database_url = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
else:
    raise ServerError('Unknown DB_TYPE variable: "{}"'.format(db_type))

app.config['DB_TYPE'] = db_type
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'max_overflow': 0,
                                           'pool_timeout': 30,
                                           'pool_recycle': 300,
                                           'pool_pre_ping': True}

db = SQLAlchemy(app, session_options={'expire_on_commit': False})

no_flask = os.environ.get('NO_FLASK')
if no_flask and int(no_flask) == 1:
    pass
else:
    import simoc_server.views
    import simoc_server.front_end_routes
