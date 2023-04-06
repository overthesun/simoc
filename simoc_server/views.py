import json
import copy
import time
import traceback
import itertools
import functools
from pathlib import Path


from flask import render_template, request, send_from_directory, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import disconnect, SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix


from simoc_server import app, db, redis_conn, redis_url
from simoc_server.database.db_model import AgentType, AgentTypeAttribute, User
from simoc_server.exceptions import GenericError, InvalidLogin, BadRequest, BadRegistration, \
    ServerError
from simoc_server.serialize import serialize_response
from simoc_server.front_end_routes import convert_configuration, load_from_basedir

from celery_worker import tasks
from celery_worker.tasks import app as celery_app

MAX_NUMBER_OF_AGENTS = 50
MAX_STEP_NUMBER = 365*24*2  # 2 Earth years

login_manager = LoginManager()
login_manager.init_app(app)

socketio = SocketIO(app, cors_allowed_origins='*', message_queue=redis_url, manage_session=False,
                    logger=app.logger)

# Fixes the issue with the SocketIO behind an Nginx proxy
# https://github.com/miguelgrinberg/Flask-SocketIO/issues/1047
app.wsgi_app = ProxyFix(app.wsgi_app)


def authenticated_only(f):
    """Decorator to check if the user is authenticated before calling the function."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


def get_steps_background(data, user_id, sid, timeout=2, max_retries=5, expire=3600):
    """Forward records from Redis to the frontend on a loop until complete."""
    if "game_id" not in data:
        raise BadRequest("game_id is required.")
    game_id = int(data["game_id"], 16)
    n_steps = int(data.get("n_steps", 1e6))
    if n_steps > 5000:
         # Increases system-wide speed by ~50% and prevents the backend crashing
         # on b2_mission1a sim.
        timeout = 5
    min_step_num = int(data.get("min_step_num", 0))
    max_step_num = min_step_num + n_steps
    # TODO: If min_step_num is not 0, batch_num should be set to the batch
    # that contains that step_num. For now, we don't allow min_step_num to be
    # set anywhere, so it hasn't been implemented yet.
    batch_num = 0 if min_step_num == 0 else None
    retries_left = max_retries
    step_count = max(0, min_step_num - 1)
    steps_sent = False
    redis_conn.set(f'sid_mapping:{sid}', game_id)
    redis_conn.expire(f'sid_mapping:{sid}', expire)
    try:
        while not steps_sent:
            socketio.sleep(timeout)
            stop_task = redis_conn.get(f'stop_task:{game_id}')
            stop_task = bool(stop_task.decode("utf-8")) if stop_task else None
            if stop_task:
                app.logger.info("Bg task closed")
                break
            output = retrieve_steps(game_id, user_id, batch_num, min_step_num, max_step_num)
            if output['n_steps'] == 0:
                retries_left -= 1
                app.logger.info(f'0 steps retrieved, {retries_left} retries left.')
            else:
                batch_num += output.pop('n_batches', 0)
                step_count += output['n_steps']
                socketio.emit('step_data_handler',
                              {'data': output, 'step_count': step_count, 'max_steps': n_steps},
                              room=sid)
                retries_left = max_retries
            if step_count >= n_steps or retries_left <= 0:
                msg = f'{step_count}/{n_steps} steps sent by the server'
                socketio.emit('steps_sent', {'message': msg}, room=sid)
                steps_sent = True
                app.logger.info(msg)
            else:
                min_step_num = step_count + 1
    finally:
        redis_conn.delete(f'sid_mapping:{sid}')


@socketio.on('connect')
def connect_handler():
    if current_user.is_anonymous:
        return False
    socketio.emit('user_connected', {'message': f'User "{current_user.username}" connected'},
                  room=request.sid)


@socketio.on('get_steps')
@authenticated_only
def get_steps_handler(message):
    """Initiate a background task to send steps to the frontend.
    
    If the user is already running a background task, it will be stopped.
    """
    if "data" not in message:
        raise BadRequest("data is required.")
    user_id = get_standard_user_obj().id
    old_game_id = redis_conn.get(f'sid_mapping:{request.sid}')
    if old_game_id:
        redis_conn.set(f'stop_task:{old_game_id}', 1)
    socketio.start_background_task(get_steps_background, message['data'], user_id, request.sid)


@socketio.on('user_disconnected')
def user_disconnected_handler():
    # the client will disconnect after sending the user_disconnected event
    user_cleanup(get_standard_user_obj())



@app.errorhandler(404)
def handle_404(e):
    # the only entry point for vue is /, attempting to go directtly to
    # other pages (such as /dashboard) will result in a 404 -- in that
    # case redirect to the root (i.e. the welcome page)
    return redirect('/')


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(Path(app.root_path, 'dist'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


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
        app.logger.info(f'User {user} logged in')
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
    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    except:
        app.logger.exception(f'Failed to create  a user "{username}".')
        db.session.rollback()
    finally:
        db.session.close()
    login_user(user)
    return status("Registration complete.")


@app.route("/unregister", methods=["POST"])
def unregister():
    """
    Deletes the user with the provided user name and password.
    Mainly used for testing.

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
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            app.logger.exception(f'Failed to delete the user "{username}".')
            db.session.rollback()
        finally:
            db.session.close()
        return status("User deleted.")
    raise InvalidLogin("Invalid username or password.")


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
    str: TBD
    """
    retries = 60
    input = json.loads(request.data.decode('utf-8'))
    if "game_config" not in input:
        raise BadRequest("game_config is required.")
    if "step_num" not in input:
        raise BadRequest("step_num is required.")
    step_num = int(input["step_num"])
    try:
        data_files = convert_configuration(input["game_config"])
        game_config, user_agent_desc, user_agent_conn = data_files
    except BadRequest as e:
        raise BadRequest(f"Cannot retrieve game config. Reason: {e}")
    if game_config['total_amount'] >= MAX_NUMBER_OF_AGENTS:
        raise BadRequest("Too many agents requested.")
    if step_num >= MAX_STEP_NUMBER:
        raise BadRequest("Too many steps requested.")
    user = get_standard_user_obj()
    user_cleanup(user)
    # Import and load default currencies list
    default_currencies = load_from_basedir('data_files/currency_desc.json')
    tasks.new_game.apply_async(args=[user.username, game_config, step_num,
                                     user_agent_desc, user_agent_conn])
    while True:
        time.sleep(0.5)
        game_id = get_user_game_id(user)
        if not game_id:
            retries -= 1
        else:
            app.logger.info(f'new_game: {user=}, {game_id=:X} '
                            f'(with {retries} retries left)')
            break
        if retries <= 0:
            msg = 'Cannot create a new game.'
            app.logger.error(msg)
            raise ServerError(msg)
    redis_conn.set('game_config:{}'.format(game_id), json.dumps(game_config))
    return status("New game starts.", game_id=format(game_id, 'X'),
                  game_config=game_config, currency_desc=default_currencies)


def get_game_config(game_id):
    """Return a game config for a given game id from Redis."""
    game_config = redis_conn.get(f'game_config:{game_id}')
    return json.loads(game_config.decode("utf-8")) if game_config else game_config

def retrieve_steps(game_id, user_id, batch_num, min_step_num, max_step_num):
    """Return all newly available batches merged together."""
    batches = []
    total_steps = 0
    batch = batch_num or 0
    while True:
        records = redis_conn.get(f'model_records:{user_id}:{game_id}:{batch}')
        if not records:
            break
        records = json.loads(records)
        steps = records.get("n_steps", 0)
        if steps == 0:
            break
        total_steps += steps
        batches.append(records)
        batch += 1
    if len(batches) == 0:
        return dict(n_steps=0, n_batches=0)
    elif len(batches) == 1:
        output = batches[0]
    elif len(batches) > 1:
        def merge_batches(b1, b2):
            if isinstance(b1, (str, int, float)):
                return b2 or b1
            elif isinstance(b1, list):
                return b1 + b2
            elif isinstance (b1, dict):
                return {k: merge_batches(b1[k], b2[k]) for k in b1.keys()}
        output = functools.reduce(lambda a, b: merge_batches(a, b), batches)
    output['n_steps'] = total_steps
    output['n_batches'] = len(batches)
    return output


def get_user_game_id(user):
    """Return a game id associated with a given user from Redis."""
    game_id = redis_conn.get(f'user_mapping:{user.id}')
    return int(game_id.decode("utf-8")) if game_id else game_id


@app.route("/get_last_game_id", methods=["POST"])
@login_required
def get_last_game_id():
    """Return the game id associated with the current user."""
    user = get_standard_user_obj()
    game_id = get_user_game_id(user)
    return status(f'Last game ID for user "{user.username}" retrieved.',
                  game_id=format(game_id, 'X'))


def kill_game_by_id(game_id):
    """Terminate a game by its id.
    
    This function performs two tasks:
    1. Revoke a Celery task of running the AgentModel
    2. Set a `stop_task` flag in Redis to stop the get_steps_background loop
    """
    redis_conn.set(f'stop_task:{game_id}', 1)
    task_id = redis_conn.get('task_mapping:{}'.format(game_id))
    task_id = task_id.decode("utf-8") if task_id else task_id
    app.logger.info(f"kill_game_by_id({game_id=:X}): revoke {task_id}")
    if task_id:
        celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')


def user_cleanup(user):
    """Terminate a game associated with a given user and delete user mapping."""
    game_id = get_user_game_id(get_standard_user_obj())
    if game_id:
        kill_game_by_id(game_id)
    redis_conn.delete('user_mapping:{}'.format(user.id))


@app.route("/kill_game", methods=["POST"])
@login_required
def kill_game():
    input = json.loads(request.data.decode('utf-8'))
    if "game_id" not in input:
        raise BadRequest("game_id is required.")
    game_id = int(input["game_id"], 16)
    kill_game_by_id(game_id)
    return status(f"Game {input['game_id']} killed.")


@app.route("/kill_all_games", methods=["POST"])
@login_required
def kill_all_games():
    """Terminate all games for all users."""
    active_workers = celery_app.control.inspect().active()
    for worker in active_workers:
        for task in active_workers[worker]:
            celery_app.control.revoke(task['id'], terminate=True, signal='SIGKILL')
    return status("All games killed.")


@app.route("/get_num_steps", methods=["POST"])
@login_required
def get_num_steps():
    input = json.loads(request.data.decode('utf-8'))
    if "game_id" not in input:
        raise BadRequest("game_id is required.")
    game_id = int(input["game_id"], 16)
    user_id = get_standard_user_obj().id
    last_record = [int(step_num) for step_num
                   in redis_conn.zrange(f'game_steps:{user_id}:{game_id}', -1, -1)][-1]
    step_num = last_record if last_record else 0
    return status("Total step number retrieved.", step_num=step_num)


@app.route("/get_agent_types", methods=["GET"])
def get_agent_types_by_class():
    """Return a list of agents for a given agent class or name.
    
    For each agent include:
    - name (e.g. 'wheat')
    - agent_class (e.g. 'plants')
    - input: list of input currencies
    - output: list of output currencies
    - characteristics: list of type/value dicts for each agent characteristic
    """
    results = []
    get_agent_class = request.args.get("agent_class", type=str)
    get_agent_name = request.args.get("agent_name", type=str)
    agent_desc = load_from_basedir('data_files/agent_desc.json')
    for agent_class, agents in agent_desc.items():
        if get_agent_class and agent_class != get_agent_class:
            continue
        for agent_name, agent_data in agents.items():
            if get_agent_name and agent_name != get_agent_name:
                continue
            entry = {"agent_class": agent_class, "name": agent_name}
            for prefix, items in agent_data['data'].items():
                for item in items:
                    if prefix not in entry:
                        entry[prefix] = []
                    if prefix in ['in', 'out']:
                        entry[prefix].append(item['type'])
                    else:
                        entry[prefix].append(
                            # FIXME: see issue #68, "units": attr.details
                            {"name": item['type'], "value": item['value']})
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


# Return the default agent_desc.json file for ACE Agent Editor
@app.route("/get_agent_desc", methods=["GET"])
def get_agent_desc():
    """Return the default agent_desc.json and agent_schema.json files."""
    agent_desc = load_from_basedir('data_files/agent_desc.json')
    agent_schema = load_from_basedir('data_files/agent_schema.json')
    return status("Agent editor data retrieved",
                  agent_desc=agent_desc, agent_schema=agent_schema)


@app.route("/get_currency_desc", methods=["GET"])
def get_currency_desc():
    """Return the default currency_desc.json file."""
    currency_desc = load_from_basedir('data_files/currency_desc.json')
    return status("Currency desc retrieved", currency_desc=currency_desc)


# TODO: This route needs to be re-designed since `worker_direct` is no longer activated
# @app.route("/save_game", methods=["POST"])
# @login_required
# def save_game():
#     """
#     Save the current game for the user.
#
#     Returns
#     -------
#     str: A success message.
#     """
#     input = json.loads(request.data.decode('utf-8'))
#     if "game_id" not in input:
#         raise BadRequest("game_id is required.")
#     if "save_name" in input:
#         save_name = str(input["save_name"])
#     else:
#         save_name = None
#     game_id = int(input["game_id"], 16)
#     # Get a direct worker queue
#     worker = redis_conn.get('worker_mapping:{}'.format(game_id)).decode("utf-8")
#     queue = worker_direct(worker)
#     # Send `save_game` for remote execution on Celery
#     tasks.save_game.apply_async(args=[get_standard_user_obj().username, save_name], queue=queue)
#     return status("Save successful.")


# TODO: Disabled until save_game is fixed
# @app.route("/load_game", methods=["POST"])
# @login_required
# def load_game():
#     """
#     Load the game with the given 'saved_game_id' on Celery Cluster.
#
#     Prints a success message.
#
#     Returns
#     -------
#     str:
#         JSON-formatted string:
#         {"game_id": "str, Game Id value", "last_step_num": "int, the last calculated step num"}
#
#     Raises
#     ------
#     simoc_server.exceptions.NotFound
#         If the SavedGame with the requested 'saved_game_id' does not exist in the database
#     """
#     retries = 30
#     input = json.loads(request.data.decode('utf-8'))
#     if "saved_game_id" not in input:
#         raise BadRequest("saved_game_id is required.")
#     if "step_num" not in input:
#         raise BadRequest("step_num is required.")
#     saved_game_id = input["saved_game_id"]
#     step_num = int(input["step_num"])
#     user = get_standard_user_obj()
#     user_cleanup(user)
#     tasks.load_game.apply_async(args=[user.username, saved_game_id, step_num])
#     while True:
#         time.sleep(0.5)
#         game_id = get_user_game_id(user)
#         if not game_id:
#             retries -= 1
#         else:
#             break
#         if retries <= 0:
#             raise ServerError(f"Cannot load a game.")
#     return status("Loaded game starts.", game_id=format(int(game_id), 'X'))


# TODO: Disabled until save_game is fixed
# @app.route("/get_saved_games", methods=["GET"])
# @login_required
# def get_saved_games():
#     """
#     Get saved games for current user. All save games fall under the root
#     branch id that they are saved under.
#
#     Returns
#     -------
#     str:
#         json format -
#
#         {
#             <root_branch_id>: [
#                 {
#                     "date_created":<date_created:str(db.DateTime)>
#                     "name": "<ave_name:str>,
#                     "save_game_id":<save_game_id:int>
#                 },
#                 ...
#             ],
#             ...
#         }
#     """
#     saved_games = SavedGame.query.filter_by(user=get_standard_user_obj()).all()
#
#     sequences = {}
#     for saved_game in saved_games:
#         snapshot = saved_game.agent_model_snapshot
#         snapshot_branch = snapshot.snapshot_branch
#         root_branch = snapshot_branch.get_root_branch()
#         if root_branch in sequences.keys():
#             sequences[root_branch].append(saved_game)
#         else:
#             sequences[root_branch] = [saved_game]
#
#     sequences = OrderedDict(
#         sorted(sequences.items(), key=lambda x: x[0].date_created))
#
#     response = {}
#     for root_branch, saved_games in sequences.items():
#         response[root_branch.id] = []
#         for saved_game in saved_games:
#             response[root_branch.id].append({
#                 "saved_game_id": saved_game.id,
#                 "name":          saved_game.name
#                 "date_created":  saved_game.date_created.strftime("%m/%d/%Y, %H:%M:%S")
#             })
#     return serialize_response(response)


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


@app.route("/ping", methods=["GET"])
def ping():
    return '', 200

