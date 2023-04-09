import argparse
import os
# import json
# import time
import logging
from logging.handlers import RotatingFileHandler

# from simoc_server import db
# from simoc_server.database.db_model import User
from simoc_server.serialize.serializer import JsonSerializer,  set_serializer


def run_flask(debug=False, port=8000, run_local=False, threaded=True, use_json=False,
              logger_level=None):
    from simoc_server import app
    addr = "0.0.0.0" if not run_local else "localhost"
    if debug:
        os.environ['PYTHONPATH'] = os.getcwd()
    if use_json:
        set_serializer(JsonSerializer)
    setup_logging(logger_level, debug)
    app.run(addr, port=port, debug=debug, threaded=threaded)


def setup_logging(logger_level, debug):
    from simoc_server import app
    if logger_level is None:
        if debug:
            logger_level = "DEBUG"
        else:
            logger_level = "INFO"
    else:
        logger_level = logger_level.upper()
    if not os.path.isdir("logs"):
        os.makedirs("logs")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler = RotatingFileHandler(os.path.join("logs", "app.log"),
                                       maxBytes=10000, backupCount=10)
    file_handler.setLevel(logger_level)
    file_handler.setFormatter(formatter)
    for handler in app.logger.handlers:
        handler.setLevel(logger_level)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logger_level)
    access_handler = RotatingFileHandler(os.path.join("logs", "access.log"),
                                         maxBytes=10000, backupCount=10)
    wsgi_logger = logging.getLogger('werkzeug')
    wsgi_logger.addHandler(access_handler)
    wsgi_logger.addHandler(file_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIMOC server.")
    parser.add_argument("--debug", action="store_true",
                        help="Run in debug mode.")
    parser.add_argument("--logger_level", "-l", type=str,
                        help="Set logger level. Defaults to INFO or DEBUG if in debug mode. Valid"
                             " logger levels include CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to run server on. Default: 8000.")
    parser.add_argument("--run_local",  action="store_true", help="Run server locally.")
    parser.add_argument("--threaded",  action="store_true",
                        help="Do not run flask app threaded.")
    parser.add_argument("--use_json",  action="store_true",
                        help="Use json to serialize rest messages, defaults to. MessagePack")
    parser.add_argument("--console_mode",  action="store_true", help="Run in console mode (no UI).")
    parser.add_argument("--username",  type=str, help="")
    parser.add_argument("--password",  type=str, help="")
    parser.add_argument("--game_config_path",  type=str, help="")
    parser.add_argument("--num_steps", type=int, default=10, help="")

    args = parser.parse_args()

    # TODO: Console Mode has to be redesign for the new Redis backend
    if not args.console_mode:
        run_flask(debug=args.debug, port=args.port, run_local=args.run_local,
                  threaded=args.threaded, use_json=args.use_json, logger_level=args.logger_level)
    # else:
    #     user = User.query.filter_by(username=args.username).first()
    #     if user:
    #         if user.validate_password(args.password):
    #             print(f"'{args.username}' logged in.")
    #         else:
    #             raise Exception('Invalid username or password.')
    #     else:
    #         print(f"Creating new user '{args.username}'.")
    #         user = User(username=args.username)
    #         user.set_password(args.password)
    #         db.session.add(user)
    #         db.session.commit()
    #     with open(args.game_config_path, 'r') as f:
    #         game_config = json.load(f)
    #     print('Initializing new simulation.')
    #     game_runner_manager = GameRunnerManager()
    #     game_runner_init_params = GameRunnerInitializationParams(game_config)
    #     game_runner_manager.new_game(user, game_runner_init_params)
    #     game_runner = game_runner_manager.get_game_runner(user)
    #     game_id = game_runner.game_id
    #
    #     print('Starting simulation.')
    #     game_runner_manager.get_step_to(user, args.num_steps)
    #     print('Simulation complete.')
    #
    #     print('Storing Model records.')
    #     ts = int(time.time())
    #     model_records = ModelRecord.query \
    #         .filter_by(user_id=user.id) \
    #         .filter_by(game_id=game_id)
    #     model_records = [i.get_all_data() for i in model_records]
    #     with open(f'{ts}_model_records.json', 'w') as f:
    #         json.dump(model_records, f)
    #     print(f'The result saved in {ts}_model_records.json.')
    #
    #     print('Storing Step records.')
    #     step_records = StepRecord.query \
    #         .filter_by(user_id=user.id) \
    #         .filter_by(game_id=game_id)
    #     step_records = [i.get_data() for i in step_records]
    #     with open(f'{ts}_step_records.json', 'w') as f:
    #         json.dump(step_records, f)
    #     print(f'The result saved in {ts}_step_records.json.')
    #
    #     print('All work is done! You can now interrupt this script.')
