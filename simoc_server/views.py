import json
import traceback
from collections import OrderedDict

from flask import request, render_template
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from simoc_server import app, db, redis_conn
from simoc_server.database.db_model import AgentType, AgentTypeAttribute, SavedGame, User, \
    ModelRecord, StepRecord
from simoc_server.exceptions import GenericError, InvalidLogin, BadRequest, BadRegistration
from simoc_server.serialize import serialize_response
from simoc_server.front_end_routes import convert_configuration, calc_step_in_out, \
    calc_step_storage_ratios, parse_step_data, count_agents_in_step, sum_agent_values_in_step

from celery_worker import tasks
from celery_worker.tasks import app as celery_app
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
        return status("Logged in.")
    raise InvalidLogin("Invalid username or password.")


@app.route("/register", methods=["POST"])
def register():
    """
    Registers the user with the provided user name and password.
    'username' and 'password' should be provided on the request
    json data. This also logs the user in.

    Returns
    -------
    str: A success message.
    """
    input = json.loads(request.data.decode('utf-8'))
    if "username" not in input:
        raise BadRegistration("Username is required.")
    if "password" not in input:
        raise BadRegistration("Password is required.")
    username = input["username"]
    password = input["password"]
    if User.query.filter_by(username=username).first():
        raise BadRegistration("User already exists.")
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return status("Registration complete.")


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
    return status("Logged out.")


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
        game_config = convert_configuration(json.loads(request.data)["game_config"])
    except BadRequest as e:
        raise BadRequest(f"Cannot retrieve game config. Reason: {e}")
    # Send `new_game` for remote execution on Celery
    result = tasks.new_game.delay(get_standard_user_obj().username, game_config).get(timeout=60)
    # Save the hostname of the Celery worker that a game was assigned to
    redis_conn.set('worker_mapping:{}'.format(result['game_id']), result['worker_hostname'])

    return status("New game starts.", game_id=result['game_id'])


@app.route("/get_steps", methods=["POST"])
@login_required
def get_steps():
    """
    Gets the step with the requested 'step_num', if not specified, uses current model step.
    total_production, total_consumption and model_stats are not calculated by default. They must be
    requested as per the examples below. By default, "agent_type_counters" and "storage_capacities"
    are included in the output, but "agent_logs" is not. If you want to change what is included, of
    these three, specify "parse_filters":[] in the input. An empty list will mean none of the three
    are included in the output.
    The following options are always returned, but if wanted could have option to filter out in
    future: {'user_id': 1, 'username': 'sinead', 'start_time': 1559046239, 'game_id': '7b966b7a',
             'step_num': 3, 'hours_per_step': 1.0, 'is_terminated': 'False', 'time': 10800.0,
             'termination_reason': None}
    Input:
       JSON specifying step_num, and the info you want included in the step_data returned

    Example 1:
    {"min_step_num": 1, "n_steps": 5, "total_production":["atmo_co2","h2o_wste"],
     "total_consumption":["h2o_wste"], "storage_ratios":{"air_storage_1":["atmo_co2"]}}
    Added to output for example 1:
    {1: {...,'total_production': {'atmo_co2': {'value': 0.128, 'unit': '1.0 kg'},
    'h2o_wste': {'value': 0.13418926977687629, 'unit': '1.0 kg'}},
    'total_consumption': {'h2o_wste': {'value': 1.5, 'unit': '1.0 kg'}},
    2:{...},...,5:{...},"storage_ratios": {"air_storage_1": {"atmo_co2": 0.00038879091443387717}}}

    Prints a success message.

    Returns
    -------
    str:
        json format -
    """
    input = json.loads(request.data.decode('utf-8'))
    if "min_step_num" not in input and "n_steps" not in input:
        raise BadRequest("min_step_num and n_steps are required.")
    if "game_id" not in input:
        raise BadRequest("game_id is required.")
    min_step_num = int(input["min_step_num"])
    n_steps = int(input["n_steps"])
    game_id = str(input["game_id"])
    max_step_num = min_step_num+n_steps-1

    # Which of the output from parse_step_data to you want returned.
    parse_filters = [] if "parse_filters" not in input else input["parse_filters"]

    user = get_standard_user_obj()
    model_record_steps = ModelRecord.query \
        .filter_by(user_id=user.id) \
        .filter_by(game_id=game_id) \
        .filter(ModelRecord.step_num >= min_step_num) \
        .filter(ModelRecord.step_num <= max_step_num).all()

    step_record_steps = StepRecord.query \
        .filter_by(user_id=user.id) \
        .filter_by(game_id=game_id) \
        .filter(StepRecord.step_num >= min_step_num) \
        .filter(StepRecord.step_num <= max_step_num).all()

    step_record_dict = dict()
    for record in step_record_steps:
        if record.step_num not in step_record_dict:
            step_record_dict[record.step_num] = [record]
        else:
            step_record_dict[record.step_num].append(record)

    output = {}
    for mri, model_record_data in enumerate(model_record_steps):
        step_num = model_record_data.step_num
        if step_num in step_record_dict:
            step_record_data = step_record_dict[step_num]
        else:
            #see issue #81. sometimes the modelrecord exists for a step but the steprecord doesn't.
            continue
        agent_model_state = parse_step_data(model_record_data, parse_filters, step_record_data)
        if "total_agent_mass" in input:
            agent_model_state["total_agent_mass"] = sum_agent_values_in_step(input["total_agent_mass"],
                                                                             'biomass_totl',
                                                                             'out',
                                                                             step_record_data)
        if "total_agent_count" in input:
            agent_model_state["total_agent_count"] = count_agents_in_step(input["total_agent_count"],
                                                                          model_record_data)
        if "total_production" in input:
            agent_model_state["total_production"] = calc_step_in_out("out",
                                                                     input["total_production"],
                                                                     step_record_data)
        if "total_consumption" in input:
            agent_model_state["total_consumption"] = calc_step_in_out("in",
                                                                      input["total_consumption"],
                                                                      step_record_data)
        if "storage_ratios" in input:
            agent_model_state["storage_ratios"] = calc_step_storage_ratios(input["storage_ratios"],
                                                                           model_record_data)
        output[int(step_num)] = agent_model_state

    return status("Step data retrieved.", step_data=output)


@app.route("/kill_game", methods=["POST"])
@login_required
def kill_game():
    input = json.loads(request.data.decode('utf-8'))
    if "game_id" not in input:
        raise BadRequest("game_id is required.")
    game_id = str(input["game_id"])
    task_id = redis_conn.get('task_mapping:{}'.format(game_id)).decode("utf-8")
    celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')
    return status(f"Game {game_id} killed.")


@app.route("/kill_all_games", methods=["POST"])
@login_required
def kill_all_games():
    active_workers = celery_app.control.inspect().active()
    for worker in active_workers:
        for task in active_workers[worker]:
            celery_app.control.revoke(task['id'], terminate=True, signal='SIGKILL')
    return status("All games killed.")


@app.route("/get_step_to", methods=["POST"])
@login_required
def get_step_to():
    """
    Schedules "step_num"  calculations on Celery cluster for the requested "game_id".

    Returns
    -------
    str: A success message.
    """
    input = json.loads(request.data.decode('utf-8'))
    if "game_id" not in input:
        raise BadRequest("game_id is required.")
    if "step_num" not in input:
        raise BadRequest("step_num is required.")
    game_id = str(input["game_id"])
    step_num = int(input["step_num"])
    # Get a direct worker queue
    worker = redis_conn.get('worker_mapping:{}'.format(game_id)).decode("utf-8")
    queue = worker_direct(worker)
    # Send `get_step_to` for remote execution on Celery
    tasks.get_step_to.apply_async(args=[get_standard_user_obj().username, step_num], queue=queue)
    return status("Steps requested.")


@app.route("/get_num_steps", methods=["POST"])
@login_required
def get_num_steps():
    input = json.loads(request.data.decode('utf-8'))
    if "game_id" not in input:
        raise BadRequest("game_id is required.")
    game_id = str(input["game_id"])
    user = get_standard_user_obj()
    last_record = ModelRecord.query \
        .filter_by(user_id=user.id) \
        .filter_by(game_id=game_id) \
        .order_by(ModelRecord.step_num.desc()) \
        .limit(1).first()
    step_num = last_record.step_num if last_record else 0
    return status("Total step number retrieved.", step_num=step_num)


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


@app.route("/save_game", methods=["POST"])
@login_required
def save_game():
    """
    Save the current game for the user.

    Returns
    -------
    str: A success message.
    """
    input = json.loads(request.data.decode('utf-8'))
    if "game_id" not in input:
        raise BadRequest("game_id is required.")
    if "save_name" in input:
        save_name = str(input["save_name"])
    else:
        save_name = None
    game_id = str(input["game_id"])
    # Get a direct worker queue
    worker = redis_conn.get('worker_mapping:{}'.format(game_id)).decode("utf-8")
    queue = worker_direct(worker)
    # Send `save_game` for remote execution on Celery
    tasks.save_game.apply_async(args=[get_standard_user_obj().username, save_name], queue=queue)
    return status("Save successful.")


@app.route("/load_game", methods=["POST"])
@login_required
def load_game():
    """
    Load the game with the given 'saved_game_id' on Celery Cluster.

    Prints a success message.

    Returns
    -------
    str:
        JSON-formatted string:
        {"game_id": "str, Game Id value", "last_step_num": "int, the last calculated step num"}

    Raises
    ------
    simoc_server.exceptions.NotFound
        If the SavedGame with the requested 'saved_game_id' does not exist in the database
    """
    input = json.loads(request.data.decode('utf-8'))
    if "saved_game_id" not in input:
        raise BadRequest("saved_game_id is required.")
    saved_game_id = input["saved_game_id"]
    # Send `load_game` for remote execution on Celery
    result = tasks.load_game.delay(get_standard_user_obj().username, saved_game_id).get(timeout=60)
    # Save the hostname of the Celery worker that a game was assigned to
    redis_conn.set('worker_mapping:{}'.format(result['game_id']), result['worker_hostname'])
    output = {"game_id": result['game_id'],
              "last_step_num": result['last_step_num']}

    return status("Loaded game starts.", **output)


@app.route("/get_saved_games", methods=["GET"])
@login_required
def get_saved_games():
    """
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
    """
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
                "date_created":  saved_game.date_created.strftime("%m/%d/%Y, %H:%M:%S")
            })
    return serialize_response(response)


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


def status(message, status_code=200, **kwargs):
    """
    Returns a status message.

    Returns
    -------
    str:
        json format -
        {
            "status":<status:str>
            "message":<status message:str>
        }

    Parameters
    ----------
    status_type : str
        A status string to send in the response
    message : str
        A message to send in the response
    status_code : int
        The status code to send on the response (default is 200)
    """
    app.logger.info(f"STATUS: {message}")
    response = {"message": message}
    for k in kwargs:
        response[k] = kwargs[k]
    response = serialize_response(response)
    response.status_code = status_code
    return response


@app.errorhandler(GenericError)
def handle_error(e):
    app.logger.error(f"ERROR: handling error {e}")
    status_code = e.status_code
    return serialize_response(e.to_dict()), status_code

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()  # print error stack
    app.logger.error(f"ERROR: handling exception {e}")
    status_code = getattr(e, 'code', 500)
    return serialize_response({'error': str(e)}), status_code


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
