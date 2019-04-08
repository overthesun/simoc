"""
These functions enable the front end to send information to where it's needed.
These functions were originally in views.py. 
"""

import json
import math

from flask import request

from simoc_server import app, db
from simoc_server.database.db_model import AgentType, AgentTypeAttribute

@app.route("/get_mass", methods=["GET"])
def get_mass():
    '''
    Sends front end mass values for config wizard.
    Takes in the request values "agent_name" and "quantity"

    Returns
    -------
    json object with total mass
    '''

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

    agent_name= request.args.get("agent_name", type=str)
    agent_quantity = request.args.get("quantity", type=int)
    attribute_name = "in_enrg_kwh"
    value_type = "energy_input"
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
            value_type = "energy_output"
        elif agent_name == "power_storage":
            attribute_name = "char_capacity_enrg_kwh"
            value_type = "energy_capacity"
        for agent in db.session.query(AgentType, AgentTypeAttribute).filter(AgentType.id == AgentTypeAttribute.agent_type_id).filter(AgentTypeAttribute.name == attribute_name).all():
            if agent.AgentType.name == agent_name:
                value = float(agent.AgentTypeAttribute.value) * agent_quantity
                total = { value_type : value}
    return json.dumps(total)


def convert_configuration(game_config):
    """This method converts the json configuration from a post into
    a more complete configuration with connections"""

    """THOMAS: This was created to allow the front end to send over a simplified version without connections. Connections are actually set up to connect to everything
    automatically, so this could use a re-haul. It also has some atmosphere values that are hard coded here that should be defined either in the agent library
    or sent from the front end. If this route is kept, most of the functionality should be moved into a separate object to help declutter and keep a solid separation
    of concerns. If it is removed, the data from the front end needs to be changed into a format based on an object similar to the one created here or in the new game view."""

    #Anything in this list will be copied as is from the input to the full_game_config. If it's not in the input it will be ignored
    labels_to_direct_copy = ["logging","priorities","minutes_per_step","location"]
    #If a game_config element should be assigned as an agent with connections: power_storage only, add it to the list below (unless you want to rename the agent, then it will need it's own code)
    #Note, this assumes power_storage is the only connection for this agent. Do not add agents which have other connections. Only agents which are present in the input game_config will be assigned
    agents_to_assign_power_storage = ["habitat","greenhouse","solar_pv_array_mars"]

    #Any agents with power_storage or food_storage will be assined power_storage = power_connections (defined later) etc. 
    #Agents initialised here must have all connections named here
    full_game_config = {"agents": {
        "human_agent":                            [
            {"connections": {"air_storage": [1], "water_storage": [1, 2], "food_storage": [1]}}],
        "solid_waste_aerobic_bioreactor":         [
            {"connections": {"air_storage":   [1], "power_storage": [1],
                             "water_storage": [1, 2], "nutrient_storage": [1]},
             "amount":      1}],
        "multifiltration_purifier_post_treament": [
            {"connections": {"water_storage": [1, 2], "power_storage": [1]}, "amount": 1}],
        "oxygen_generation_SFWE":                 [
            {"connections": {"air_storage": [1], "power_storage": [1], "water_storage": [1, 2]},
             "amount":      1}],
        "urine_recycling_processor_VCD":          [
            {"connections": {"power_storage": [1], "water_storage": [1, 2]}, "amount": 1}],
        "co2_removal_SAWD":                       [
            {"connections": {"air_storage": [1], "power_storage": [1]}, "amount": 1}],
        "co2_reduction_sabatier":                 [
            {"connections": {"air_storage": [1], "power_storage": [1], "water_storage": [1, 2]},
             "amount":      1}]
        # "particulate_removal_TCCS" : [{"connections":{"air_storage": [1],"power_storage": [1]},"amount":1}]
    },
        "storages":               {
            "air_storage":      [
                {"id":       1, "atmo_h2o": 10, "atmo_o2": 2100, "atmo_co2": 3.5, "atmo_n2": 7886,
                 "atmo_ch4": 0.009531,
                 "atmo_h2":  0.005295}],
            "water_storage":    [{"id": 1, "h2o_potb": 5000, "h2o_tret": 1000},
                                 {"id": 2, "h2o_potb": 4000, "h2o_wste": 100, "h2o_urin": 100}],
            "nutrient_storage": [{"id": 1, "sold_n": 100, "sold_p": 100, "sold_k": 100}],
            "power_storage":    [],
            "food_storage":     []},
        "termination":            [
            {"condition": "evacuation"}]}
    food_storage_capacity = int(
        db.session.query(
            AgentType, AgentTypeAttribute).filter(
            AgentType.id == AgentTypeAttribute.agent_type_id).filter(
            AgentTypeAttribute.name == "char_capacity_food_edbl").first().AgentTypeAttribute.value)
    food_storage_amount = math.ceil(
        (game_config["food_storage"]["amount"]) / (int(food_storage_capacity)))


    #This is where labels from labels_to_direct_copy are copied directly from game_config to full_game_config
    for labeldc in labels_to_direct_copy:
        if labeldc in game_config:
            full_game_config[labeldc] = game_config[labeldc]

    #Assign termination values
    if (game_config["duration"]):
        duration = {
            "condition": "time",
            "value":     game_config["duration"]["value"],
            "unit":      game_config["duration"]["type"]}
        full_game_config["termination"].append(duration)

    #is it a single agent
    full_game_config["single_agent"] = 1 if ('single_agent' in game_config and game_config["single_agent"] == 1) else 0

    #The rest of this function is for reformatting agents.
    #food_connections and power_connections will be assigned to all agents with food_storage or power_storage respecitively, at the end of this function.

    #Determine the food and power connections to be assigned to all agents with food and power storage later
    power_storage_amount = game_config["power_storage"]["amount"]
    food_connections, power_connections = [], []
    food_left = game_config["food_storage"]["amount"]
    for x in range(1, int(food_storage_amount) + 1):
        food_connections.append(x)
        if (food_left > food_storage_capacity):
            full_game_config["storages"]["food_storage"].append(
                {"id": x, "food_edbl": food_storage_capacity})
            food_left -= food_storage_capacity
        else:
            full_game_config["storages"]["food_storage"].append(
                {"id": x, "food_edbl": food_left})

    for y in range(1, int(power_storage_amount) + 1):
        power_connections.append(y)
        full_game_config["storages"]["power_storage"].append(
            {"id": y, "enrg_kwh": 0})


    #Here, agents from agents_to_assign_power_storage are assigned with only a power_storage connection.
    for labelps in agents_to_assign_power_storage:
        if (game_config[labelps]):
            amount = 1 if not "amount" in game_config[labelps] else game_config[labelps]["amount"]
            full_game_config["agents"][game_config[labelps]] = [
                {"connections": {"power_storage": [1]}, "amount": amount}]

    #If the front_end specifies an amount for this agent, overwrite any default values with the specified value
    for x, y in full_game_config["agents"].items():
        if x in game_config and "amount" in game_config[x]:
            y[0]["amount"] = game_config[x]["amount"]

    #Plants are treated separately because its a list of items which must be assigned as agents
    if (game_config["plants"]):
        for plant in game_config["plants"]:
            full_game_config["agents"][plant["species"]] = [
                {"connections": {"air_storage": [1], "water_storage": [
                    1, 2], "nutrient_storage":  [1], "power_storage": [], "food_storage": [1]},
                 "amount":      plant["amount"]}]


    #Here, power connections and food connections are assigned to all agents with power_storage or food_storage specified. 
    for x, y in full_game_config["agents"].items():
        if "power_storage" in y[0]["connections"]:
            y[0]["connections"]["power_storage"] = power_connections
        if "food_storage" in y[0]["connections"]:
            y[0]["connections"]["food_storage"] = food_connections

    return (full_game_config)
