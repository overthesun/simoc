import datetime
import os
from collections import OrderedDict
from uuid import uuid4

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, session, send_from_directory, safe_join, Flask, render_template

from simoc_server import app, db
from simoc_server.serialize import serialize_response, deserialize_request, data_format_name
from simoc_server.database.db_model import User, SavedGame
from simoc_server.agent_model.agent_name_mapping import agent_name_mapping
from simoc_server.game_runner import GameRunner
from simoc_server import error_handlers


login_manager = LoginManager()
login_manager.init_app(app)

game_runners = {}

@app.before_request
def deserialize_before_request():
    deserialize_request(request)

@app.route("/")
def home():
    return render_template('panel_content.html')

@app.route("/loginpanel", methods=["GET"])
def loginpanel():
    return render_template("panel_login.html")

@app.route("/registerpanel", methods=["GET"])
def registerpanel():
    return render_template("panel_register.html")

@app.route("/gameinit", methods=["GET"])
def gameinit():
    return render_template("base_game.html")

@app.route("/data_format", methods=["GET"])
def data_format():
    return data_format_name()

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
    simoc_server.error_handlers.InvalidLogin
        If the user with the given username or password cannot
        be found.
    '''
    print(request.deserialized)
    username = request.deserialized["username"]
    password = request.deserialized["password"]
    user = User.query.filter_by(username=username).first()
    if user and user.validate_password(password):
        login_user(user)
        return success("Logged In.")
    raise error_handlers.InvalidLogin("Bad username or password.")

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
    simoc_server.error_handlers.BadRegistration
        If the user already exists.
    '''
    if request.deserialized is None:
        raise error_handlers.BadRequest("No data or malformed data in request.")
    if "username" not in request.deserialized.keys():
        raise error_handlers.BadRequest("Username not found in request content.")
    if "password" not in request.deserialized.keys():
        raise error_handlers.BadRequest("Password not found in request content.")
    username = request.deserialized["username"]
    password = request.deserialized["password"]
    if(User.query.filter_by(username=username).first()):
        raise error_handlers.BadRegistration("User already exists")
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
    a game runner to 'game_runners'.

    Returns
    -------
    str: A success message.
    '''
    game_runner = GameRunner.from_new_game(current_user)
    add_game_runner(game_runner)
    return success("New game created.")

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
    print(request.url)
    print(request.args)
    step_num = request.args.get("step_num", type=int)
    game_runner = get_game_runner()
    agent_model_state = game_runner.get_step(step_num)
    return serialize_response(agent_model_state)

@app.route("/save_game", methods=["POST"])
@login_required
def save_game():
    '''
    Save the current game for the session.

    Returns
    -------
    str :
        A success message.
    '''
    if "save_name" in request.deserialized.keys():
        save_name = request.deserialized["save_name"]
    else:
        save_name = None
    game_runner = get_game_runner()
    game_runner.save_game(save_name)
    return success("Save successful.")

@app.route("/load_game", methods=["POST"])
@login_required
def load_game():
    '''
    Load game with given 'saved_game_id' in session.  Adds
    GameRunner to game_runners.

    Returns
    -------
    str:
        A success message.

    Raises
    ------
    simoc_server.error_handlers.BadRequest
        If 'saved_game_id' is not in the json data on the request.

    simoc_server.error_handlers.NotFound
        If the GameRunner with the requested 'saved_game_id' does not
        exist in game_runners dictionary

    '''

    # TODO cleanup old GameRunners
    if "saved_game_id" in request.deserialized.keys():
        saved_game_id = request.deserialized["saved_game_id"]
    else:
        raise error_handlers.BadRequest("Required value 'saved_game_id' not found in request.")
    saved_game = SavedGame.query.get(saved_game_id)
    if saved_game is None:
        raise error_handlers.NotFound("Requested game not found in loaded games.")
    game_runner = GameRunner.load_from_saved_game(saved_game)
    add_game_runner(game_runner)
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
    saved_games = SavedGame.query.filter_by(user=current_user).all()

    sequences = {}
    for saved_game in saved_games:
        snapshot = saved_game.agent_model_snapshot
        snapshot_branch = snapshot.snapshot_branch
        root_branch = snapshot_branch.get_root_branch()
        if(root_branch in sequences.keys()):
            sequences[root_branch].append(save_game)
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

@app.route("/sprite_mappings", methods=["GET"])
def sprite_mappings():
    '''
    Get sprite mapping rules for all agents.
    Returns
    -------
    str:
        json format -
        {
            <agent_type_name> : {
                "default_sprite": <path_to_default_sprite:str>
                "rules": [
                    {
                        "comparator":{
                            "attr_name":<agent_attribute_name:str>,
                            "op":<comparison_operator:str>,
                            "value":<comparison_value>
                        },
                        "offset_x":<offset_x_value_for_placing_sprite:str>,
                        "offset_y":<offset_y_value_for_placing_sprite:str>,
                        "precedence": <precedence_for_rule:int>,
                        "sprite_path":<path_to_sprite:str>
                    },
                    ...
                ]
            },
            ...
        }
    '''
    response = {}
    for key, val in agent_name_mapping.items():
        response[key] = val.__sprite_mapper__().to_serializable()
    print(response)
    return serialize_response(response)

@app.route("/sprite/<path:sprite_path>", methods=["GET"])
def get_sprite(sprite_path):
    '''
    Returns a sprite at the requested path.  Paths are provided
    by rules given in '/sprite_mappings' route

    Returns
    -------
        response : Contains requested image.

    Parameters
    ----------
    sprite_path : str
        The path to the sprite
    '''
    print(sprite_path)
    root_path = "res/sprites"
    full_path = safe_join(app.root_path, root_path, sprite_path)
    if not os.path.isfile(full_path):
        print(full_path)
        raise error_handlers.NotFound("Requested sprite not found: {0}".format(sprite_path))
    return send_from_directory(root_path, sprite_path)

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


def get_game_runner():
    '''
    Returns the game runner for the active session

    Returns
    -------
        simoc_server.game_runner.GameRunner
    Raises
    ------
    simoc_server.error_handlers.BadRequest
        If there is there is not 'game_runner_id' in the session
        attached to the request.
    simoc_server.error_handlers.NotFound
        If the GameRunner with the requested id is not found.
    '''
    if "game_runner_id" not in session.keys():
        raise error_handlers.BadRequest("No game found in session.")
    game_runner_id = session["game_runner_id"]
    if game_runner_id not in game_runners.keys():
        raise error_handlers.NotFound("Game not found.")
    game_runner = game_runners[game_runner_id]
    return game_runner

def add_game_runner(game_runner):
    '''
     Adds a game runner to the internal game runner collection

    Returns
    -------
        int : The key for the game runner in the 'game_runners' dict.

    Parameters
    ----------
     game_runner : simoc_server.game_runner.GamerRunner
        the game_runner to add
    '''

    # TODO Cleanup gamerunner on logout
    game_runner_id = uuid4()
    game_runners[game_runner_id] = game_runner
    session["game_runner_id"] = game_runner_id
    return game_runner_id

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
    print(message)
    response = serialize_response(
        {
            "message":message
        })
    response.status_code = status_code
    return response
