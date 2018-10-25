import datetime
import os

import json

from flask_cors import CORS

from collections import OrderedDict
from uuid import uuid4

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, session, send_from_directory, safe_join, render_template

from simoc_server import app, db
from simoc_server.serialize import serialize_response, deserialize_request, data_format_name
from simoc_server.database.db_model import User, SavedGame
from simoc_server.game_runner import (GameRunner, GameRunnerManager,
        GameRunnerInitializationParams)

from simoc_server.exceptions import InvalidLogin, BadRequest, \
    BadRegistration, NotFound, GenericError

login_manager = LoginManager()
login_manager.init_app(app)

cors = CORS(app, resources={r"/*":{"origins": "*"}},supports_credentials="true")

game_runner_manager = None

@app.before_first_request
def create_game_runner_manager():
    global game_runner_manager
    game_runner_manager = GameRunnerManager()

#@app.before_first_request

def create_game_runner_manager():
    global game_runner_manager
    game_runner_manager = GameRunnerManager()

@app.before_request
def deserialize_before_request():
    deserialize_request(request)

@app.route("/test_route", methods=["GET","POST"])
def testroute():

    return render_template('partial_dashboard.html',static_url_path='/static')

@app.route("/test_route2", methods=["GET","POST"])
def testroute2():
    return render_template('test.html')


@app.route("/")
def home():
    return render_template('index.html')

#@app.route("/loginpanel", methods=["GET"])
#def loginpanel():
 #   return render_template("panel_login.html")

@app.route("/registerpanel", methods=["GET"])
def registerpanel():
    return render_template("base_registration.html")

@app.route("/gameinit", methods=["GET"])
def gameinit():
    return render_template("base_template.html",content=content)

@app.route("/data_format", methods=["GET"])
def data_format():
    return data_format_name()

@app.route("/loginvue", methods=["POST"])
def loginvue():
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

    user_info = json.loads(request.data)

    user = User.query.filter_by(username=user_info['username']).first()
    if user and user.validate_password(user_info['password']):
        login_user(user)
        return success("Logged In.")
    raise InvalidLogin("Bad username or password")

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
    username = try_get_param("username")
    password = try_get_param("password")
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
    #username = try_get_param("username")
    #password = try_get_param("password")
    user_info = json.loads(request.data)

    username = user_info['username']
    password = user_info['password']

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
#@login_required
def new_game():
    '''
    Creates a new game on the current session and adds
    a game runner to the game_runner_manager

    Returns
    -------
    str: A success message.
    '''
    # TODO add real configuration parameters
    mode          = try_get_param("mode")
    launch_date   = try_get_param("launch_date")
    duration_days = try_get_param("duration_days")
    payload       = try_get_param("payload")
    location      = try_get_param("location")
    region        = try_get_param("region")
    regolith      = try_get_param("regolith")

    AGENTS = {
        "greenhouse_medium": 1,
        "human_agent": 1,
        "cabbage": 10,
        'lettuce': 10,
        'solar_pv_array': 10,
        'multifiltration_purifier_post_treament': 10
    }

    STORAGES = {
        "air_storage": 2,
        "water_storage": 1,
        "nutrient_storage": 1,
        "power_storage": 1,
        "food_storage": 1
    }

    game_runner_init_params = GameRunnerInitializationParams(AGENTS, STORAGES)
    game_runner_manager.new_game(get_standard_user_obj(), game_runner_init_params)
    return success("New Game Starts")

@app.route("/new_game_vue", methods=["POST"])
#@login_required
def new_game_vue():
    '''
    Creates a new game on the current session and adds
    a game runner to the game_runner_manager
    Returns
    -------
    str: A success message.
    '''

    try:
        game_config = try_get_param("game_config")
    except BadRequest as e:
        game_config = {"agents": {
            "human_agent": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "nutrient_storage": [1],
                                            "power_storage": [1], "food_storage": [1]}, "amount": 2}],
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
            "nutrient_storage": [{"id": 1, "sold_n": 100, "sold_p": 100, "sold_k": 100, "sold_wast": 0}],
            "power_storage": [{"id": 1, "enrg_kwh": 1000, "heat_cal": 1000}],
            "food_storage": [{"id": 1, "food_edbl": 200}]},
        "termination": {
            "time": {"value":168 , "unit": "hour"}},
            "food_leaf": {"value": 10000, "unit": "kg"},
            "evacuation": {}
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
        {
            "step_num":<agent_model_step_number>,
            "agents": [
                {
                    "id":<agent_unique_id:str>,
                    "agent_type":<agent_type_name:str>,
                    "pos_x":<position_x_coordinate:int>,
                    "pos_y":<position_y_coordinate:int>,
                    "attributes": {
                        <attribute_name:str>:<value>,
                        ...
                    }
                },
                ...
            ]
        }


    '''
    step_num = request.args.get("step_num", type=int)
    agent_model_state = game_runner_manager.get_step(get_standard_user_obj(), step_num)
    print(json.dumps(agent_model_state))

    #return serialize_response(agent_model_state)
    return(json.dumps(agent_model_state))
@app.route("/save_game", methods=["POST"])
@login_required
def save_game():
    '''
    Save the current game for the user.

    Returns
    -------
    str :
        A success message.
    '''
    if "save_name" in request.deserialized.keys():
        save_name = request.deserialized["save_name"]
    else:
        save_name = None
    game_runner_manager.save_game(get_standard_user_obj() ,save_name)
    return success("Save successful.")

@app.route("/load_game", methods=["POST"])
@login_required
def load_game():
    '''
    Load game with given 'saved_game_id' in session.  Adds
    GameRunner to game_runner_manager.

    Returns
    -------
    str:
        A success message.

    Raises
    ------
    simoc_server.exceptions.BadRequest
        If 'saved_game_id' is not in the json data on the request.

    simoc_server.exceptions.NotFound
        If the SavedGame with the requested 'saved_game_id' does not
        exist in the database

    '''

    saved_game_id = try_get_param("saved_game_id")
    saved_game = SavedGame.query.get(saved_game_id)
    if saved_game is None:
        raise NotFound("Requested game not found in loaded games.")
    game_runner_manager.load_game(get_standard_user_obj(), saved_game)
    return success("Game loaded successfully.")

@app.route("/get_saved_games", methods=["GET"])
@login_required
def get_saved_games():
    '''
    Get saved games for current user. All save games fall under the root
    branch id that they are saved under.

    Returns
    -------
    str:
        json format -

        {
            <root_branch_id>: [
                {
                    "date_created":<date_created:str(db.DateTime)>
                    "name": "<ave_name:str>,
                    "save_game_id":<save_game_id:int>
                },
                ...
            ],
            ...
        }


    '''
    saved_games = SavedGame.query.filter_by(user=get_standard_user_obj()).all()

    sequences = {}
    for saved_game in saved_games:
        snapshot = saved_game.agent_model_snapshot
        snapshot_branch = snapshot.snapshot_branch
        root_branch = snapshot_branch.get_root_branch()
        if root_branch in sequences.keys():
            sequences[root_branch].append(saved_game)
        else:
            sequences[root_branch] = [saved_game]

    sequences = OrderedDict(sorted(sequences.items(), key=lambda x: x[0].date_created))

    response = {}
    for root_branch, saved_games in sequences.items():
        response[root_branch.id] = []
        for saved_game in saved_games:
            response[root_branch.id].append({
                "saved_game_id":saved_game.id,
                "name":saved_game.name,
                "date_created":saved_game.date_created
            })
    return serialize_response(response)

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