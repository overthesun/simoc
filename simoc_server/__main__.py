import argparse
import os
import traceback
import logging
from logging.handlers import RotatingFileHandler

from simoc_server.serialize.serializer import JsonSerializer, MsgPackSerializer, set_serializer
from simoc_server.agent_model import AgentModel
from simoc_server import app
from simoc_server import exit_handler

def run(debug=False, port=8000, run_local=False, threaded=True, 
        use_json=False, logger_level=None, logger_level_file=None):
    addr = "0.0.0.0" if not run_local else "localhost"
    if debug:
        os.environ['PYTHONPATH'] = os.getcwd()
    if use_json:
        set_serializer(JsonSerializer)
    setup_logging(logger_level, logger_level_file, debug)
    app.run(addr, port=port, debug=debug, threaded=threaded)

def setup_logging(logger_level, logger_level_file, debug):
    if logger_level is None:
        if debug:
            logger_level = "DEBUG"
        else:
            logger_level = "INFO"
    else:
        logger_level = logger_level.upper()
    if logger_level_file is None:
        logger_level_file = logger_level
    else:
        logger_level_file = logger_level_file.upper()
    if not os.path.isdir("logs"):
        os.makedirs("logs")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler = RotatingFileHandler(os.path.join("logs", "app.log"), maxBytes=10000, backupCount=10)
    file_handler.setLevel(logger_level)
    file_handler.setFormatter(formatter)

    for handler in app.logger.handlers:
        handler.setLevel(logger_level)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logger_level)

    # access log
    access_handler = RotatingFileHandler(os.path.join("logs", "access.log"), maxBytes=10000, backupCount=10)
    wsgi_logger = logging.getLogger('werkzeug')
    wsgi_logger.addHandler(access_handler)
    wsgi_logger.addHandler(file_handler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIMOC server.")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode.")
    parser.add_argument("--logger_level", "-l", type=str, help="Set logger level. Defaults to INFO or DEBUG if in debug mode."
            " Valid logger levels include CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET")
    parser.add_argument("--logger_level_file", "-lf", type=str, help="Set logger level. Defaults to logger_level value.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on. Default: 8000.")
    parser.add_argument("--run_local",  action="store_true", help="Run server locally.")
    parser.add_argument("--do_not_thread",  action="store_true", help="Do not run flask app threaded.")
    parser.add_argument("--use_json",  action="store_true", help="Use json to serialize rest messages, defaults to."
        "MessagePack")

    args = parser.parse_args()
    run(debug=args.debug, port=args.port, run_local=args.run_local, threaded=(not args.do_not_thread), use_json=args.use_json,
        logger_level=args.logger_level, logger_level_file=args.logger_level_file)
