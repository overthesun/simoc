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


def convert_configuration(config_obj):
    """This method converts the json configuration from a post into
    a more complete configuration with connections"""

    """THOMAS: This was created to allow the front end to send over a simplified version without connections. Connections are actually set up to connect to everything
    automatically, so this could use a re-haul. It also has some atmosphere values that are hard coded here that should be defined either in the agent library
    or sent from the front end. If this route is kept, most of the functionality should be moved into a separate object to help declutter and keep a solid separation
    of concerns. If it is removed, the data from the front end needs to be changed into a format based on an object similar to the one created here or in the new game view."""

    game_config = config_obj
    full_game_config = {"agents": {
        "human_agent":                            [
            {"connections": {"air_storage": [1], "water_storage": [1, 2]}}],
        "solid_waste_aerobic_bioreactor":         [
            {"connections": {"air_storage":   [1], "power_storage": [1],
                             "water_storage": [1, 2], "nutrient_storage": [1]},
             "amount":      1}],
        "multifiltration_purifier_post_treament": [
            {"connections": {"water_storage": [1, 2]}, "amount": 1}],
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

    if 'logging' in game_config:
        full_game_config['logging'] = game_config['logging']

    if 'priorities' in game_config:
        full_game_config['priorities'] = game_config['priorities']

    if 'minutes_per_step' in game_config:
        full_game_config['minutes_per_step'] = game_config['minutes_per_step']

    if 'location' in game_config:
        full_game_config['location'] = game_config['location']

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

    for x, y in full_game_config["agents"].items():
        if x == "human_agent":
            continue
        else:
            y[0]["connections"]["power_storage"] = power_connections
    if (game_config["human_agent"]):
        full_game_config["agents"]["human_agent"][0]["amount"] = game_config["human_agent"][
            "amount"]
        full_game_config["agents"]["human_agent"][0]["connections"][
            "food_storage"] = food_connections
    if (game_config["duration"]):
        duration = {
            "condition": "time",
            "value":     game_config["duration"]["value"],
            "unit":      game_config["duration"]["type"]}
        full_game_config["termination"].append(duration)
    if (game_config["plants"]):
        for plant in game_config["plants"]:
            full_game_config["agents"][plant["species"]] = [
                {"connections": {"air_storage": [1], "water_storage": [
                    1, 2], "nutrient_storage":  [1], "power_storage": [], "food_storage": [1]},
                 "amount":      plant["amount"]}]
            full_game_config["agents"][plant["species"]
            ][0]["connections"]["food_storage"] = food_connections
            full_game_config["agents"][plant["species"]
            ][0]["connections"]["power_storage"] = power_connections
    if (game_config["habitat"]):
        full_game_config["agents"][game_config["habitat"]] = [
            {"connections": {"power_storage": [1]}, "amount": 1}]
        full_game_config["agents"][game_config["habitat"]
        ][0]["connections"]["power_storage"] = power_connections
    if (game_config["greenhouse"]):
        full_game_config["agents"][game_config["greenhouse"]] = [
            {"connections": {"power_storage": [1]}, "amount": 1}]
        full_game_config["agents"][game_config["greenhouse"]
        ][0]["connections"]["power_storage"] = power_connections
    if (game_config["solar_arrays"]):
        full_game_config["agents"]["solar_pv_array_mars"] = [{"connections": {
            "power_storage": [1]}, "amount":                                 game_config[
                                                                                 "solar_arrays"][
                                                                                 "amount"]}]
        full_game_config["agents"]["solar_pv_array_mars"][0]["connections"][
            "power_storage"] = power_connections
    if ('single_agent' in game_config and game_config["single_agent"] == 1):
        full_game_config["single_agent"] = 1
    else:
        full_game_config["single_agent"] = 0
    return (full_game_config)
