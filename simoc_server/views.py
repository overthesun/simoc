import datetime
import os
from collections import OrderedDict
from uuid import uuid4

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, session, send_from_directory, safe_join, render_template

from simoc_server import app, db
from simoc_server.serialize import serialize_response, deserialize_request, data_format_name
from simoc_server.database.db_model import User, SavedGame
from simoc_server.agent_model.agents import agent_name_mapping
from simoc_server.game_runner import (GameRunner, GameRunnerManager,
        GameRunnerInitializationParams)

from simoc_server.exceptions import InvalidLogin, BadRequest, \
    BadRegistration, NotFound, GenericError

login_manager = LoginManager()
login_manager.init_app(app)

game_runner_manager = GameRunnerManager()

start={
'show':'show', #Show pane
'active':'active', #Active State
'id':'start', #HREF
'title':'Step 1: Welcome To SIMOC', 
'formid':'wizardform',

'radioOne':{'roworder':'1','display':'visible','label':'Scientific','value':'Scientific','id':'Scientific','group':'Mode'},

'radioTwo':{'roworder':'2','display':'visible','label':'Interactive','value':'Interactive','id':'Interactive','group':'Mode'},

'radioThree':{'roworder':'3','display':'none','label':'TestingRadio','value':'TestingRadio','id':'TestingRadio','group':''},

'select':{'roworder':'4','display':'visible','label':'Testing','id':'TestingSelect', 'options':[{'value':'value','label':'Value'}]},
'integer':{'roworder':'5','display':'visible','label':'TestingInteger','id':'TestingInteger'},

'checkbox':{'roworder':'5','display':'visible','label':'Permanent','id':'permanent'},

'ipbutton':{'roworder':'6','display':'visible','label':'Test Button','id':'','state':'active','class':'Test-Button'},

'cancelButton':{'btnOneState':'active','btnOneLabel':'Cancel','btnOneClass':'cancel-step'},

'navButton':{'btnOneState':'disabled','btnOneLabel':'Previous','btnOneClass':'previous-step','btnTwoState':'active','btnTwoLabel':'Next','btnTwoClass':'next-step'},

'information':'Welcome to SIMOC, a scalable model of an isolated, off-world community. Here you will enjoy the challenges and rewards of growing your habitat to a thriving city, or exploring the surrounding terrain with a limited crew. Whatever your mode of operation, be warned that closed ecosystems are a delicate thing, easy to unbalance and difficult to recover. Select from Play Mode or Science Run. In Play Mode you will interact regularly, making decisions that alter the course of the growth of your community. In a Science Run you will configure the model up-front and let it run its full course without interaction, then collect the data when done.', #Information Section
}

configuration={
'show':'show', #Show pane
'active':'disabled', #Active State
'id':'configuration', #HREF
'title':'Step 2: Welcome To SIMOC', 
'formid':'wizardform',

'radioOne':{'roworder':'1','display':'visible','label':'Testing One','id':'Testing One','group':'model'},

'radioTwo':{'roworder':'2','display':'visible','label':'Testing Two','id':'Testing Two','group':'model'},

'radioThree':{'roworder':'3','display':'visible','label':'TestingThree','id':'Testing Radio 3','group':''},

'select':{'roworder':'4','display':'visible','label':'Testing','id':'configuration',
    'options':
        [{'value':'SIMOC Baseline','label':'SIMOC Baseline'},
        {'value':"NASA 'Astronaut In A Can'",'label':"NASA 'Astronaut In A Can'"},
        {'value':"Mars One",'label':"Mars One"}]},

'integer':{'roworder':'5','display':'visible','label':'TestingInteger','id':'duration'},

'checkbox':{'roworder':'5','display':'visible','label':'Permanent','id':'permanent'},

'ipbutton':{'roworder':'6','display':'visible','label':'Test Button','id':'','state':'active','class':'Test-Button'},

'cancelButton':{'btnOneState':'active','btnOneLabel':'Cancel','btnOneClass':'cancel-step'},

'navButton':{'btnOneState':'disabled','btnOneLabel':'Previous','btnOneClass':'previous-step','btnTwoState':'active','btnTwoLabel':'Next','btnTwoClass':'next-step'},

'information':'This is a test', #Information Section
}

finalize={
'show':'show', #Show pane
'active':'', #Active State
'id':'finalize', #HREF
'title':'Step 10: Finalize', 
'formid':'wizardform',

'cancelButton':{'btnOneState':'active','btnOneLabel':'Cancel','btnOneClass':'cancel-step'},

'navButton':{'btnOneState':'active','btnOneLabel':'Previous','btnOneClass':'previous-step','btnTwoState':'active','btnTwoLabel':'Finalize','btnTwoClass':'finalize-step'},

'information':'This is a test', #Information Section
}

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
    return render_template('templatewizard.html',start=start,configuration=configuration,finalize=finalize)

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
    username = try_get_param("username")
    password = try_get_param("password")
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


@app.route("/test_route",methods=["POST"])
def test_route():
    return success("You made it!")

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

    game_runner_init_params = GameRunnerInitializationParams(mode, launch_date,
        duration_days, payload, location, region, regolith)
    game_runner_manager.new_game(get_standard_user_obj(), game_runner_init_params)
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
    step_num = request.args.get("step_num", type=int)
    agent_model_state = game_runner_manager.get_step(get_standard_user_obj(), step_num)
    return serialize_response(agent_model_state)

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
        # initialize the sprite mapper class and serialize it
        response[key] = val._sprite_mapper().to_serializable()
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
        raise NotFound("Requested sprite not found: {0}".format(sprite_path))
    return send_from_directory(root_path, sprite_path)

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
    print(message)
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