import json
import math

from flask import after_this_request, request
from io import StringIO as IO
import gzip
import functools 


from flask_compress import Compress

from collections import OrderedDict

from flask import request, render_template
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from simoc_server import app, db
from simoc_server.database.db_model import AgentType, AgentTypeAttribute, AgentTypeAttributeDetails, SavedGame, User
from simoc_server.exceptions import InvalidLogin, BadRequest, BadRegistration, \
    GenericError, NotFound
from simoc_server.game_runner import (GameRunnerManager, GameRunnerInitializationParams)
from simoc_server.serialize import serialize_response, data_format_name
from simoc_server.front_end_routes import convert_configuration,calc_step_in_out, calc_step_storage_ratios

login_manager = LoginManager()
login_manager.init_app(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials="true")

game_runner_manager = None


@app.before_first_request
def create_game_runner_manager():
    global game_runner_manager
    game_runner_manager = GameRunnerManager()

@app.route("/")
def home():
    return render_template('index.html')

'''
@app.route("/data_format", methods=["GET"])
def data_format():
    return data_format_name()
'''

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
    userinfo = json.loads(request.data.decode('utf-8'))
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
    userinfo = json.loads(request.data.decode('utf-8'))
    username = userinfo["username"]
    password = userinfo["password"]
    if (User.query.filter_by(username=username).first()):
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

    Prints a success message

    Returns
    -------
    str: The game ID
    '''

    try:
        game_config = convert_configuration(
            json.loads(request.data)["game_config"])
    except BadRequest as e:
        print("Cannot retrieve game config. Reason: {}".format(e))
        start_data = {'game_config': {'duration':      {'type': 'day', 'value': 30},
                                      'food_storage':  {'amount': 1000},
                                      'greenhouse':    'greenhouse_small',
                                      'habitat':       'crew_habitat_small',
                                      'human_agent':   {'amount': 1},
                                      'logging':       {'columns': ['agent_id',
                                                                    'agent_type',
                                                                    'value',
                                                                    'unit'],
                                                        'filters': [('currency', ['enrg_kwh']),
                                                                    ('direction', ['in'])]},
                                      'plants':        [{'amount': 1, 'species': 'rice'}],
                                      'power_storage': {'amount': 1},
                                      'priorities':    ['inhabitants', 'eclss', 'plants',
                                                        'storage'],
                                      'solar_arrays':  {'amount': 1}}}
        game_config = convert_configuration(start_data["game_config"])

    game_runner_init_params = GameRunnerInitializationParams(game_config)
    game_runner_manager.new_game(
        get_standard_user_obj(),
        game_runner_init_params)

    #get game ID
    game_runner = game_runner_manager.get_game_runner(get_standard_user_obj())
    game_id = game_runner.game_id

    success("New Game Starts")
    return game_id


@app.route("/get_step", methods=["POST"])
@login_required
def get_step():
    '''
    Gets the step with the requsted 'step_num', if not specified,
        uses current model step.

    total_production, total_consumption and model_stats are not calculated by default. 
    They must be requested as per the examples below.

    By default, "agent_type_counters" and "storage_capacities" are included in the output, but "agent_logs" is not. If you want to change what is included, of these three, specify "parse_filters":[] in the input. An empty list will mean none of the three are included in the output.

    The following options are always returned, but if wanted could have option to filter out in future: {'user_id': 1, 'username': 'sinead', 'start_time': 1559046239, 'game_id': '7b966b7a', 'step_num': 3, 'hours_per_step': 1.0, 'is_terminated': 'False', 'time': 10800.0, 'termination_reason': None}

    Input:
       JSON specifying step_num, and the info you want included in the step_data returned
       

    Example 1:
    {"min_step_num": 1, "n_steps": 5, "total_production":["atmo_co2","h2o_wste"],"total_consumption":["h2o_wste"],"storage_ratios":{"air_storage_1":["atmo_co2"]}}
    Added to output for example 1: 
    {1: {...,'total_production': {'atmo_co2': {'value': 0.128, 'unit': '1.0 kg'}, 'h2o_wste': {'value': 0.13418926977687629, 'unit': '1.0 kg'}}, 'total_consumption': {'h2o_wste': {'value': 1.5, 'unit': '1.0 kg'}}, 2:{...},...,5:{...},"storage_ratios": {"air_storage_1": {"atmo_co2": 0.00038879091443387717}}}

    Returns
    -------
    str:
        json format -
    '''

    input = json.loads(request.data)
#    input = {"min_step_num": 1, "n_steps": 3, "total_production":["atmo_co2","h2o_wste"],"total_consumption":["h2o_wste"],"storage_ratios":{"air_storage_1":["atmo_co2"]},"parse_filters":[]}
#    get_step_to()

    if not "min_step_num" in input and not "n_steps" in input:
        sys.exit("ERROR: min_step_num and n_steps are required as input to views.get_step() route")
    min_step_num = int(input["min_step_num"])
    n_steps = int(input["n_steps"])

    #FIXME: this should come from the front end (gets passed to front end in new_game route)
    if not "game_id" in input:
        game_runner = game_runner_manager.get_game_runner(get_standard_user_obj())
        game_id = game_runner.game_id
    else:
        game_id = input["game_id"]

    #Which of the output from game_runner.parse_step_data to you want returned. 
    parse_filters=["agent_type_counters","storage_capacities"] if not "parse_filters" in input else input["parse_filters"]

    output = {}
    for step_num in range(min_step_num,min_step_num+n_steps):
        agent_model_state = game_runner_manager.get_step(
            get_standard_user_obj(), game_id, step_num,parse_filters)
    
        if "total_production" in input:
            agent_model_state["total_production"] = calc_step_in_out(step_num,"out",input["total_production"]) 
        if "total_consumption" in input:
            agent_model_state["total_consumption"] = calc_step_in_out(step_num,"in",input["total_consumption"])
        if "storage_ratios" in input:
            agent_model_state["storage_ratios"] = calc_step_storage_ratios(step_num,input["storage_ratios"])

        output[int(step_num)] = agent_model_state

    response = json.dumps(output)
    response = response.encode('utf-8')
    response = gzip.compress(response)
    return response



@app.route("/get_step_to", methods=["GET"])
@login_required
def get_step_to():
    step_num = request.args.get("step_num", type=int)
    game_runner_manager.get_step_to(get_standard_user_obj(), step_num)

    return success("Steps Created")


@app.route("/get_batch_steps", methods=["GET"])
@login_required
def get_batch_steps():
    batch_size, batch = request.args.get("step_batch_size", type=int), []
    for i in range(batch_size):
        state = game_runner_manager.get_step(get_standard_user_obj())
        batch.append(state)
    return json.dumps(batch)


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
                entry[prefix].append(
                    {"name": currency, "value": attr.value})#FIXME: see issue #68, "units": attr.details})
        results.append(entry)
    return json.dumps(results)

# @app.route("/get_agents_by_category", methods=["GET"])
# def get_agents_by_category():
#     '''
#     Gets the names of agents with the specified category characteristic.
#
#     Returns
#     -------
#     array of strings.
#     '''

#     """THOMAS: Should probably hand functionality off to a separate object, to maintain separation of concerns."""

#     results = []
#     agent_category = request.args.get("category", type=str)
#     for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentTypeAttribute.name == "char_category").filter(AgentTypeAttribute.value == agent_category).filter(AgentType.id == AgentTypeAttribute.agent_type_id).all():
#         results.append(agent.AgentType.name)
#     return json.dumps(results)

@app.route("/get_agents_by_category", methods=["GET"])
def get_agents_by_category():
    '''
    Gets the names of agents with the specified category characteristic.

    Returns
    -------
    array of strings.
    '''
    results = []
    agent_category = request.args.get("category", type=str)
    for agent in db.session.query(
            AgentType, AgentTypeAttribute).filter(
        AgentTypeAttribute.name == "char_category").filter(
        AgentTypeAttribute.value == agent_category).filter(
        AgentType.id == AgentTypeAttribute.agent_type_id).all():
        results.append(agent.AgentType.name)
    return json.dumps(results)


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
    game_runner_manager.save_game(get_standard_user_obj(), save_name)
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

    sequences = OrderedDict(
        sorted(sequences.items(), key=lambda x: x[0].date_created))

    response = {}
    for root_branch, saved_games in sequences.items():
        response[root_branch.id] = []
        for saved_game in saved_games:
            response[root_branch.id].append({
                "saved_game_id": saved_game.id,
                "name":          saved_game.name,
                "date_created":  saved_game.date_created
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
            "message": message
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
        if (request.deserialized is None):
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
