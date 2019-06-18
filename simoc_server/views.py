import json
import sys

from flask import request, render_template
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from simoc_server import app, db, redis_conn
from simoc_server.database.db_model import AgentType, AgentTypeAttribute, User, \
    ModelRecord, StepRecord
from simoc_server.exceptions import InvalidLogin, BadRequest, BadRegistration, \
    GenericError
from simoc_server.serialize import serialize_response
from simoc_server.front_end_routes import convert_configuration, calc_step_in_out, \
    calc_step_storage_ratios, parse_step_data

from celery_worker import tasks
from celery.utils import worker_direct

login_manager = LoginManager()
login_manager.init_app(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials="true")


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/login", methods=["POST"])
def login():
    """
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
    """
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
    """
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
    """
    userinfo = json.loads(request.data.decode('utf-8'))
    username = userinfo["username"]
    password = userinfo["password"]
    if User.query.filter_by(username=username).first():
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
    """
    Logs current user out.

    Returns
    -------
    str: A success message.
    """
    logout_user()
    return success("Logged Out.")


@app.route("/new_game", methods=["POST"])
@login_required
def new_game():
    """
    Creates a new game on Celery cluster.

    Prints a success message.

    Returns
    -------
    str: The Game ID
    """
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
    # Send `new_game` for remote execution on Celery
    print(game_config)
    print('new_game request received')
    result = tasks.new_game.delay(get_standard_user_obj().username, game_config).get(timeout=60)
    print('new_game task finished')
    # Save the hostname of the Celery worker that a game was assigned to
    redis_conn.set('worker_mapping:{}'.format(result['game_id']), result['worker_hostname'])
    print('Mapping updated: {}: {}'.format('worker_mapping:{}'.format(result['game_id']),
                                           result['worker_hostname']))
    success("New Game Starts")
    return result['game_id']


@app.route("/get_steps", methods=["POST"])
@login_required
def get_steps(game_id):
    """
        TBD
    """
    input = json.loads(request.data)

    if "min_step_num" not in input and "n_steps" not in input:
        sys.exit("ERROR: min_step_num and n_steps are required as input to views.get_step() route")
    min_step_num = int(input["min_step_num"])
    n_steps = int(input["n_steps"])
    max_step_num = min_step_num+n_steps-1

    # Which of the output from parse_step_data to you want returned.
    parse_filters = ["agent_type_counters", "storage_capacities"] if "parse_filters" not in input \
        else input["parse_filters"]

    user = get_standard_user_obj()
    model_record_steps = ModelRecord.query \
        .filter_by(user_id=user.id) \
        .filter_by(game_id=game_id) \
        .filter(ModelRecord.step_num >= min_step_num) \
        .filter(ModelRecord.step_num <= max_step_num)

    step_record_steps = None
    if len(parse_filters) > 0 or "total_production" in input or "total_consumption" in input:
        step_record_steps = StepRecord.query \
            .filter_by(user_id=user.id) \
            .filter_by(game_id=game_id) \
            .filter(StepRecord.step_num >= min_step_num) \
            .filter(StepRecord.step_num <= max_step_num)
            
    output = {}
    for mri, model_record_data in enumerate(model_record_steps):
        step_num = model_record_data.step_num
        agent_model_state = parse_step_data(model_record_data,parse_filters)
        if "total_production" in input or "total_consumption" in input:
            step_record = step_record_steps.filter_by(step_num=step_num)
            if "total_production" in input:
                agent_model_state["total_production"] = calc_step_in_out(step_num,
                                                                         "out",
                                                                         input["total_production"],
                                                                         step_record)
            if "total_consumption" in input:
                agent_model_state["total_consumption"] = calc_step_in_out(step_num,
                                                                          "in",
                                                                          input["total_consumption"],
                                                                          step_record)
        if "storage_ratios" in input:
            agent_model_state["storage_ratios"] = calc_step_storage_ratios(step_num,
                                                                           input["storage_ratios"],
                                                                           model_record_data)
        output[int(step_num)] = agent_model_state

    return json.dumps(output)


@app.route("/get_step_to", methods=["GET"])
@login_required
def get_step_to(game_id):
    step_num = request.args.get("step_num", type=int)
    # Get a direct worker queue
    worker = redis_conn.get('worker_mapping:{}'.format(game_id))
    queue = worker_direct(worker)
    # Send `get_step_to` for remote execution on Celery
    tasks.get_step_to.apply_async(args=[get_standard_user_obj().username, step_num], queue=queue)
    return success("Steps Created")


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
                    # FIXME: see issue #68, "units": attr.details
                    {"name": currency, "value": attr.value})
        results.append(entry)
    return json.dumps(results)


@app.route("/get_agents_by_category", methods=["GET"])
def get_agents_by_category():
    """
    Gets the names of agents with the specified category characteristic.

    Returns
    -------
    array of strings.
    """
    results = []
    agent_category = request.args.get("category", type=str)
    for agent in db.session.query(AgentType, AgentTypeAttribute). \
            filter(AgentTypeAttribute.name == "char_category"). \
            filter(AgentTypeAttribute.value == agent_category). \
            filter(AgentType.id == AgentTypeAttribute.agent_type_id).all():
        results.append(agent.AgentType.name)
    return json.dumps(results)


@login_manager.user_loader
def load_user(user_id):
    """
    Method used by flask-login to get user with requested id

    Parameters
    ----------
    user_id : str
        The requested user id.
    """
    return User.query.get(int(user_id))


def success(message, status_code=200):
    """
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
    """
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
        if request.deserialized is None:
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
