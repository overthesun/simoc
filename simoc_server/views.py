import datetime
import os
import json


from collections import OrderedDict
from uuid import uuid4

from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, session, send_from_directory, safe_join, render_template

from simoc_server.database.db_model import AgentType
from simoc_server import app, db
from simoc_server.serialize import serialize_response, deserialize_request, data_format_name
from simoc_server.database.db_model import User, SavedGame
from simoc_server.game_runner import (GameRunner, GameRunnerManager,
        GameRunnerInitializationParams)

from simoc_server.exceptions import InvalidLogin, BadRequest, \
    BadRegistration, NotFound, GenericError

login_manager = LoginManager()
login_manager.init_app(app)

game_runner_manager = None

cors = CORS(app, resources={r"/*":{"origins": "*"}},supports_credentials="true")

@app.before_first_request
def create_game_runner_manager():
    global game_runner_manager
    game_runner_manager = GameRunnerManager()

#@app.before_request
#def deserialize_before_request():
#    deserialize_request(request)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/gameinit", methods=["GET"])
def gameinit():
    return render_template("base_template.html",content=content)

@app.route("/login", methods=["POST"])
def login():
    '''
    Logs the user in with the provided user name and password.
    'username' and 'password' should be provided on the request
    json data.

    Returns
    -------
    str: A success message.

    Raises
    ------
    simoc_server.exceptions.InvalidLogin
        If the user with the given username or password cannot
        be found.
    '''
    userinfo = json.loads(request.data)
    username = userinfo["username"]
    password = userinfo["password"]
    user = User.query.filter_by(username=username).first()
    if user and user.validate_password(password):
        login_user(user)
        return success("Logged In.")
    raise InvalidLogin("Bad username or password.")

@app.route("/register", methods=["POST"])
def register():
    '''
    Registers the user with the provided user name and password.
    'username' and 'password' should be provided on the request
    json data. This also logs the user in.

    Returns
    -------
    str: A success message.

    Raises
    ------
    simoc_server.exceptions.BadRegistration
        If the user already exists.
    '''
    userinfo = json.loads(request.data)
    username = userinfo["username"]
    password = userinfo["password"]
    if(User.query.filter_by(username=username).first()):
        raise BadRegistration("User already exists")
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return success("Registration complete.")

@app.route("/logout")
@login_required
def logout():
    '''
    Logs current user out.

    Returns
    -------
    str: A success message.
    '''
    logout_user()
    return success("Logged Out.")


@app.route("/new_game", methods=["POST"])
@login_required
def new_game():
    '''
    Creates a new game on the current session and adds
    a game runner to the game_runner_manager

    Returns
    -------
    str: A success message.
    '''
    user_config = json.loads(request.data)
    try:
        game_config = user_config['game_config']
    except BadRequest as e:
        game_config = {"agents": {
            "human_agent": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "food_storage": [1]}, "amount": 20}],
            "cabbage": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "nutrient_storage": [1],
                                         "power_storage": [1], "food_storage": [1]}, "amount": 10}],
            "lettuce": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "nutrient_storage": [1],
                                         "power_storage": [1], "food_storage": [1]}, "amount": 10}],
            "greenhouse_medium": [{"connections": {"power_storage": [1]}, "amount": 1}],
            "solar_pv_array": [{"connections": {"power_storage": [1]}, "amount": 100}],
            "multifiltration_purifier_post_treament": [{"connections": {"water_storage": [1, 2]}, "amount": 1}],
            "urine_recycling_processor_VCD": [{"connections": {"power_storage": [1], "water_storage": [1, 2]}, "amount": 1}]},
        "storages": {
            "air_storage": [{"id": 1, "atmo_h2o": 100, "atmo_o2": 100, "atmo_co2": 100}],
            "water_storage": [{"id": 1, "h2o_potb": 100, "h2o_tret": 100}, {"id": 2, "h2o_wste": 100, "h2o_urin": 100}],
            "nutrient_storage": [{"id": 1, "sold_n": 100, "sold_p": 100, "sold_k": 100}],
            "power_storage": [{"id": 1, "enrg_kwh": 1000}],
            "food_storage": [{"id": 1, "food_edbl": 200}]},
        "termination": [
            {"condition": "time", "value": 2, "unit": "year"},
            {"condition": "food_leaf", "value": 10000, "unit": "kg"},
            {"condition": "evacuation"}]
        }
        print("Cannot retrieve game config. Reason: {}".format(e))
        print("Using default config: {}".format(game_config))

    game_runner_init_params = GameRunnerInitializationParams(game_config)
    game_runner_manager.new_game(get_standard_user_obj(), game_runner_init_params)
    return success("New Game Starts")

@app.route("/get_step", methods=["GET"])
@login_required
def get_step():
    '''
    Gets the step with the requsted 'step_num', if not specified,
        uses current model step.

    Returns
    -------
    str:
        json format -
    '''
    step_num = request.args.get("step_num", type=int)
    agent_model_state = game_runner_manager.get_step(get_standard_user_obj(), step_num)
    return json.dumps(agent_model_state)

@app.route("/get_agent_types", methods=["GET"])
def get_agent_types_by_class():
    args, results = {}, []
    agent_class = request.args.get("agent_class", type=str)
    agent_name = request.args.get("agent_name", type=str)
    if agent_class:
        args["agent_class"] = agent_class
    if agent_name:
        args["name"] = agent_name
    for agent in AgentType.query.filter_by(**args).all():
        entry = {"agent_class": agent.agent_class, "name": agent.name}
        for attr in agent.agent_type_attributes:
            prefix, currency = attr.name.split('_', 1)
            if prefix not in entry:
                entry[prefix] = []
            if prefix in ['in', 'out']:
                entry[prefix].append(currency)
            else:
                entry[prefix].append({"name": currency, "value": attr.value, "units": attr.units})
        results.append(entry)
    return serialize_response(results)

@app.route("/ping", methods=["GET", "POST"])
def ping():
    """Ping the server to prevent clean up of active game
    """
    game_runner_manager.ping(get_standard_user_obj())
    return success("Pong")

@login_manager.user_loader
def load_user(user_id):
    '''
    Method used by flask-login to get user with requested id

    Parameters
    ----------
    user_id : str
        The requested user id.
    '''
    return User.query.get(int(user_id))

def success(message, status_code=200):
    '''
    Returns a success message.

    Returns
    -------
    str:
        json format -
        {
            "message":<success message:str>
        }

    Parameters
    ----------
    message : str
        A string to send in the response
    status_code : int
        The status code to send on the response (default is 200)
    '''
    app.logger.info("Success: {}".format(message))
    response = serialize_response(
        {
            "message":message
        })
    response.status_code = status_code
    return response

@app.errorhandler(GenericError)
def handle_error(error):
    """Handles GenericError type exceptions
    
    Parameters
    ----------
    error : GenericError
        Error thrown
    
    Returns
    -------
    Serialized Response
        The response to send to the client
    """
    if error.status_code >= 500:
        app.logger.error(error.message)
    response = serialize_response(error.to_dict())
    response.status_code = error.status_code
    return response

def try_get_param(name):
    """Attempts to retrieve named value from
    request parameters

    Parameters
    ----------
    name : str
        The name of the parameter to retrieve

    Returns
    -------
    Type of param
        The value of the param to retreive.

    Raises
    ------
    BadRequest
        If the named param is not found in the request or
        if there is no params in the request.
    """
    try:
        return request.deserialized[name]
    except TypeError as e:
        if(request.deserialized is None):
            raise BadRequest("No params on request or params are malformed, "
                "'{}' is a required param.".format(name))
        else:
            raise e
    except KeyError:
        raise BadRequest("'{}' not found in request parameters.".format(name))

def get_standard_user_obj():
    """This method should be used instead of 'current_user'
    to prevent issues arising when the user object is accessed
    later on.  'current_user' is actually of type LocalProxy
    rather than 'User'.

    Returns
    -------
    simoc_server.database.db_model.User
        The current user entity for the request.
    """
    return current_user._get_current_object()