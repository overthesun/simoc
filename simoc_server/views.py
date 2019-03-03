import datetime
import os
import json
import math
from collections import OrderedDict
from uuid import uuid4

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, session, send_from_directory, safe_join, render_template
from flask_cors import CORS
from simoc_server.database.db_model import AgentType, AgentTypeAttribute
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

#@app.before_request
#def deserialize_before_request():
 #   deserialize_request(request)

content={'formid':'wizardform',
'wizard':{
'startInformation':'Welcome to SIMOC, a scalable model of an isolated, off-world community. Here you will enjoy the challenges and rewards of growing your habitat to a thriving city, or exploring the surrounding terrain with a limited crew. Whatever your mode of operation, be warned that closed ecosystems are a delicate thing, easy to unbalance and difficult to recover.',
'startInformationp2':'Select from Play Mode or Science Run. In Play Mode you will interact regularly, making decisions that alter the course of the growth of your community. In a Science Run you will configure the model up-front and let it run its full course without interaction, then collect the data when done.',
'configurationInformation':'Select from Preset models or Configure your own SIMOC community. The Preset models are each based upon a real-world experiment or base-line configuration. They require very little input and as such, the outcome is anticipated within a certain margin of error. These are used primarily for Science Runs. If you select to Configure your own model, you will be taken step-by-step through the panels in this Configuration Wizard.',
'locationInformation':'Where you place your initial habitat and build your community is perhaps the single most important decision made. In Earth orbit you are just hours away from a launch pad and supplies and realtime communications. On the Moon things become more challenging, yet you remain relatively close to home where an evacuation puts you safely on terra firma within a matter of days. But on Mars, in the asteroid belt, or on the distant moons of Jupiter or Saturn you are months from home even with the fastest rocket available. Truly isolated, successful in situ resource utilization may be the difference between success and failure.',
'regionInformation':'Within the Location you must choose where on the celestial body you desire to place your foundational habitat. You may take into consideration the overall mission objective: to grow a massive, thriving city, to conduct geologic exploration, or to search for life.',
'terrainInformation':'Your mission may be to explore a unique geological area, but that same area is devoid of water in relatively dry soil, forcing you to import water or extract it from a distant region at the cost of fuel for transport. With regolith rich in minerals you can more rapidly build new structures. With longer days you gain more energy by means of solar panels.',
'launchInformation':'Select the date of launch and how long your crew remains at the habitat dictates whether you are to rely solely upon imported goods and supplies, or those enabled through in situ resource utilization.',
'transportationInformation':'Select the type of rocket, resulting in how long it takes to arrive to the destination. A shorter flight consumes more fuel and thereby forces a smaller payload. A longer flight enables more humans and/or supplies, but requires more time to arrive.',
'payloadInformation':'Select a balance between cargo (goods, machinery, habitat modules, food and water stores) and humans. This is governed by the total kilograms (Kg) of carrying capacity for the given rocket. The user must select the number of humans taken along for the ride, which invokes a certain mass of water, food, and breathable atmosphere. What remains is for cargo.',
'modelInformation':'The Model defines the basic mode of operation, and the underlying algorithm that will govern the growth policy of the community. Based upon the prior screen (PAYLOAD), the system will auto-select provisions, rovers, structures, manufacturing equipment. These are listed as preloaded configurations. In a later version, the player can manually select the specific payload.'
}}


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
    #userinfo = json.loads(request.data)
    print(request.data)
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
    #userinfo = json.loads(request.data)
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

    try:
        game_config = convert_configuration(json.loads(request.data)["game_config"])
            
    except BadRequest as e:
        game_config = {"agents": {
            "human_agent": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "food_storage": [1]}, "amount": 4}],
            "cabbage": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "nutrient_storage": [1],
                                         "power_storage": [1], "food_storage": [1]}, "amount": 10}],
            "lettuce": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "nutrient_storage": [1],
                                         "power_storage": [1], "food_storage": [1]}, "amount": 10}],
            "rice": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "nutrient_storage": [1],
                                         "power_storage": [1], "food_storage": [1]}, "amount": 10}],
            "celery": [{"connections": {"air_storage": [1], "water_storage": [1, 2], "nutrient_storage": [1],
                                         "power_storage": [1], "food_storage": [1]}, "amount": 10}],
            "greenhouse_medium": [{"connections": {"power_storage": [1]}, "amount": 1}],
            "crew_habitat_small": [{"connections": {"power_storage": [1]}, "amount": 1}],
            "solar_pv_array_mars": [{"connections": {"power_storage": [1]}, "amount": 20}],
            "solid_waste_aerobic_bioreactor": [{"connections": {"air_storage": [1],"power_storage": [1], "water_storage": [1, 2],"nutrient_storage": [1]}, "amount": 1}],
            "multifiltration_purifier_post_treament": [{"connections": {"water_storage": [1, 2]}, "amount": 1}],
            "oxygen_generation_SFWE" : [{"connections": {"air_storage": [1],"power_storage": [1], "water_storage": [1, 2]}, "amount": 1}],
            "urine_recycling_processor_VCD": [{"connections": {"power_storage": [1], "water_storage": [1, 2]}, "amount": 1}],
            "co2_removal_SAWD":[{"connections":{"air_storage": [1],"power_storage": [1]},"amount":1}],
            "co2_reduction_sabatier":[{"connections":{"air_storage": [1],"power_storage": [1], "water_storage": [1, 2]},"amount":1}],
            "particulate_removal_TCCS" : [{"connections":{"air_storage": [1],"power_storage": [1]},"amount":1}]},
        "storages": {
            "air_storage": [{"id": 1, "atmo_h2o": 0, "atmo_o2": 210, "atmo_co2": 10,"atmo_n2":780}],
            "water_storage": [{"id": 1, "h2o_potb": 400, "h2o_tret": 100}, {"id": 2, "h2o_potb": 400, "h2o_wste": 100, "h2o_urin": 100}],
            "nutrient_storage": [{"id": 1, "sold_n": 100, "sold_p": 100, "sold_k": 100}],
            "power_storage": [{"id": 1, "enrg_kwh": 1000}],
            "food_storage": [{"id": 1, "food_edbl": 200}]},
        "termination": [
            {"condition": "time", "value": 30, "unit": "day"},
            {"condition": "food_leaf", "value": 10000, "unit": "kg"},
            {"condition": "evacuation"}]
        }
        #print("Cannot retrieve game config. Reason: {}".format(e))     
        
    #Next 2 lines are for testing only
    #start_data ={"game_config": {"duration" : {"value": 1, "type" : "years"},"human_agent": {"amount" : 1},"habitat" : "crew_habitat_small","greenhouse" : "greenhouse_large","food_storage":{"amount" : 1000}, "plants" : [{"species" : "spinach", "amount": 10}, {"species": "cabbage", "amount" : 10}], "solar_arrays" : {"amount":50}, "power_storage" : {"amount":10}, "single_agent" : 1}}
    #game_config = convert_configuration(start_data["game_config"])

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

@app.route("/get_batch_steps", methods=["GET"])
@login_required
def get_batch_steps():
    batch_size, batch = request.args.get("step_batch_size", type=int), []
    for i in range(batch_size):
        state = game_runner_manager.get_step(get_standard_user_obj())
        batch.append(state)
    return json.dumps(batch)

@app.route("/get_logs", methods=["GET"])
@login_required
def get_logs():
    filters = request.args.get("filters", [])
    columns = request.args.get("columns", [])
    agent_model = game_runner_manager.get_game_runner(get_standard_user_obj()).agent_model
    logs = agent_model.get_logs(filters=filters, columns=columns, dtype='list')
    return json.dumps(logs)

@app.route("/get_step_logs", methods=["GET"])
@login_required
def get_step_logs():
    step_num = request.args.get("step_num", None)
    filters = request.args.get("filters", [])
    columns = request.args.get("columns", [])
    agent_model = game_runner_manager.get_game_runner(get_standard_user_obj()).agent_model
    logs = agent_model.get_step_logs(step_num, filters=filters, columns=columns, dtype='list')
    return json.dumps(logs)

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

@app.route("/get_agents_by_category", methods=["GET"])
def get_agents_by_category():
    '''
    Gets the names of agents with the specified category characteristic.

    Returns
    -------
    array of strings.
    '''

    """THOMAS: Should probably hand functionality off to a separate object, to maintain separation of concerns."""

    results = []
    agent_category = request.args.get("category", type=str)
    for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentTypeAttribute.name == "char_category").filter(AgentTypeAttribute.value == agent_category).filter(AgentType.id == AgentTypeAttribute.agent_type_id).all():   
        results.append(agent.AgentType.name)
    return json.dumps(results)

@app.route("/get_mass", methods=["GET"])
def get_mass():
    '''
    Sends front end mass values for config wizard.
    Takes in the request values "agent_name" and "quantity"

    Returns
    -------
    json object with total mass
    '''

    """THOMAS: Should probably hand functionality off to a separate object, to maintain separation of concerns."""

    value = 0
    agent_name = request.args.get("agent_name", type=str)
    agent_quantity = request.args.get("quantity", type=int)
    if not agent_quantity:
        agent_quantity = 1
    if agent_name == "eclss":
        total = 0
        for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentType.id == AgentTypeAttribute.agent_type_id).filter(AgentTypeAttribute.name == "char_mass").filter(AgentType.agent_class == "eclss").all():
            total += float(agent.AgentTypeAttribute.value)
        value = total 
    else:
        for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentType.id == AgentTypeAttribute.agent_type_id).filter(AgentTypeAttribute.name == "char_mass").all():
            if agent.AgentType.name == agent_name:
                value = float(agent.AgentTypeAttribute.value)
    value = value * agent_quantity
    total = { "mass" : value} 
    return json.dumps(total)

@app.route("/get_energy", methods=["GET"])
def get_energy():
    '''
    Sends front end energy values for config wizard.
    Takes in the request values "agent_name" and "quantity"

    Returns
    -------
    json object with energy value for agent
    '''

    """THOMAS: Should probably hand functionality off to a separate object, to maintain separation of concerns."""
    agent_name= request.args.get("agent_name", type=str)
    agent_quantity = request.args.get("quantity", type=int)
    attribute_name = "in_enrg_kwh"
    value_type = "energy input"
    total = {}
    if not agent_quantity:
        agent_quantity = 1
    if agent_name == "eclss":
        total_eclss = 0
        for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentType.id == AgentTypeAttribute.agent_type_id).filter(AgentTypeAttribute.name == "in_enrg_kwh").filter(AgentType.agent_class == "eclss").all():
            total_eclss += float(agent.AgentTypeAttribute.value)
        value = total_eclss * agent_quantity
        total = {value_type : value}
    else:
        if agent_name == "solar_pv_array_mars":
            attribute_name = "out_enrg_kwh"
            value_type = "energy output"
        elif agent_name == "power_storage":
            attribute_name = "char_capacity_enrg_kwh"
            value_type = "energy capacity"
        for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentType.id == AgentTypeAttribute.agent_type_id).filter(AgentTypeAttribute.name == attribute_name).all():
            if agent.AgentType.name == agent_name:
                value = float(agent.AgentTypeAttribute.value) * agent_quantity
                total = { value_type : value}
    return json.dumps(total)

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

def convert_configuration(config_obj):
    """This method converts the json configuration from a post into
    a more complete configuration with connections"""

    """THOMAS: This was created to allow the front end to send over a simplified version without connections. Connections are actually set up to connect to everything
    automatically, so this could use a re-haul. It also has some atmosphere values that are hard coded here that should be defined either in the agent library
    or sent from the front end. If this route is kept, most of the functionality should be moved into a separate object to help declutter and keep a solid separation
    of concerns. If it is removed, the data from the front end needs to be changed into a format based on an object similar to the one created here or in the new game view."""

    game_config = config_obj
    full_game_config = {"agents": {
        "human_agent": [{"connections": {"air_storage": [1], "water_storage": [1]}}],
        "solid_waste_aerobic_bioreactor": [{"connections": {"air_storage": [1],"power_storage": [1], "water_storage": [1],"nutrient_storage": [1]}, "amount": 1}],
        "multifiltration_purifier_post_treament": [{"connections": {"water_storage": [1, 2]}, "amount": 1}],
        "oxygen_generation_SFWE" : [{"connections": {"air_storage": [1],"power_storage": [1], "water_storage": [1]}, "amount": 1}],
        "urine_recycling_processor_VCD": [{"connections": {"power_storage": [1], "water_storage": [1]}, "amount": 1}],
        "co2_removal_SAWD":[{"connections":{"air_storage": [1],"power_storage": [1]},"amount":1}],
        "co2_reduction_sabatier":[{"connections":{"air_storage": [1],"power_storage": [1], "water_storage": [1]},"amount":1}]
        #Particulate removal was removed for the time being
        #"particulate_removal_TCCS" : [{"connections":{"air_storage": [1],"power_storage": [1]},"amount":1}]
        },
    "storages": {
        "air_storage": [{"id": 1, "atmo_h2o": 10, "atmo_o2": 2100, "atmo_co2": 3.5,"atmo_n2":7886, "atmo_ch4" : 0.009531, "atmo_h2" : 0.005295}],
        "water_storage": [{"id": 1, "h2o_potb": 5000, "h2o_tret": 1000, "h2o_wste": 100, "h2o_urin": 100}],
        "nutrient_storage": [{"id": 1, "sold_n": 100, "sold_p": 100, "sold_k": 100}],
        "power_storage": [],
        "food_storage": []},
    "termination": [
        {"condition": "evacuation"}]}
    food_storage_capacity = int(db.session.query(AgentType, AgentTypeAttribute).filter(AgentType.id == AgentTypeAttribute.agent_type_id).filter(AgentTypeAttribute.name == "char_capacity_food_edbl").first().AgentTypeAttribute.value)
    food_storage_amount = math.ceil((game_config["food_storage"]["amount"])/(int(food_storage_capacity)))

    if 'logging' in game_config:
        full_game_config['logging'] = game_config['logging']

    if 'priorities' in game_config:
        full_game_config['priorities'] = game_config['priorities']

    power_storage_amount = game_config["power_storage"]["amount"]
    food_connections, power_connections = [], []
    food_left = game_config["food_storage"]["amount"]
    for x in range(1, int(food_storage_amount)+1):
        food_connections.append(x)
        if(food_left > food_storage_capacity):
            full_game_config["storages"]["food_storage"].append({"id" : x, "food_edbl" : food_storage_capacity})
            food_left -= food_storage_capacity
        else:
            full_game_config["storages"]["food_storage"].append({"id" : x, "food_edbl" : food_left})

    for y in range(1, int(power_storage_amount)+1):
        power_connections.append(y)
        full_game_config["storages"]["power_storage"].append({"id" : y, "enrg_kwh" : 0})

    for x,y in full_game_config["agents"].items():
        if x == "human_agent":
            continue
        else:
            y[0]["connections"]["power_storage"] = power_connections
    if(game_config["human_agent"]):
        full_game_config["agents"]["human_agent"][0]["amount"]=game_config["human_agent"]["amount"]
        full_game_config["agents"]["human_agent"][0]["connections"]["food_storage"] = food_connections
    if(game_config["duration"]):
        duration = {"condition": "time", "value": game_config["duration"]["value"], "unit": game_config["duration"]["type"]}
        full_game_config["termination"].append(duration)
    if(game_config["plants"]):
        for plant in game_config["plants"]:

            full_game_config["agents"][plant["species"]] = [{"connections": {"air_storage": [1], "water_storage": [1, 2], "nutrient_storage": [1],"power_storage": [], "food_storage": [1]}, "amount": plant["amount"]}]
            full_game_config["agents"][plant["species"]][0]["connections"]["food_storage"] = food_connections
            full_game_config["agents"][plant["species"]][0]["connections"]["power_storage"] = power_connections
    if(game_config["habitat"]):
        full_game_config["agents"][game_config["habitat"]] = [{"connections": {"power_storage": [1]}, "amount": 1}]
        full_game_config["agents"][game_config["habitat"]][0]["connections"]["power_storage"] = power_connections
    if(game_config["greenhouse"]):
        full_game_config["agents"][game_config["greenhouse"]] = [{"connections": {"power_storage": [1]}, "amount": 1}]
        full_game_config["agents"][game_config["greenhouse"]][0]["connections"]["power_storage"] = power_connections
    if(game_config["solar_arrays"]):

        full_game_config["agents"]["solar_pv_array_mars"] = [{"connections": {"power_storage": [1]}, "amount": game_config["solar_arrays"]["amount"]}]
        full_game_config["agents"]["solar_pv_array_mars"][0]["connections"]["power_storage"] = power_connections
    if('single_agent' in game_config and game_config["single_agent"] == 1):
        full_game_config["single_agent"] = 1
    else:
        full_game_config["single_agent"] = 0
    return(full_game_config)