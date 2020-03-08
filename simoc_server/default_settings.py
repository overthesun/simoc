import os

SECRET_KEY = os.environ.get('FLASK_SECRET', 't00p__s3cr3t!?')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 10,
                             'max_overflow': 0,
                             'pool_timeout': 30,
                             'pool_recycle': 300,
                             'pool_pre_ping': True}
JSONIFY_PRETTYPRINT_REGULAR = False
JSON_SORT_KEYS = False
