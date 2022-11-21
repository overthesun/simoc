"""
These functions perform calculations or assignments which
are to be passed back to the front end, but none of the functions
are called directly from the front end.
These functions were originally in views.py.
The front end routes which call the functions here are in views.py
Note: the name of this script is misleading and should be changed
"""

import json
import math
import sys
import datetime
import pathlib
import copy

from flask import request

from simoc_server import app, db, redis_conn
from simoc_server.database.db_model import AgentType, AgentTypeAttribute


@app.route('/get_mass', methods=['GET'])
def get_mass():
    """
    Sends front end mass values for config wizard.
    Takes in the request values 'agent_name' and 'quantity'

    Returns
    -------
    json object with total mass
    """

    value = 0
    agent_name = request.args.get('agent_name', type=str)
    agent_quantity = request.args.get('quantity', 1, type=int) or 1
    if agent_name == 'eclss':
        total = 0
        for agent in db.session.query(AgentType, AgentTypeAttribute) \
          .filter(AgentType.id == AgentTypeAttribute.agent_type_id) \
          .filter(AgentTypeAttribute.name == 'char_mass') \
          .filter(AgentType.agent_class == 'eclss').all():
            total += float(agent.AgentTypeAttribute.value)
        value = total
    else:
        for agent in db.session.query(AgentType, AgentTypeAttribute) \
          .filter(AgentType.id == AgentTypeAttribute.agent_type_id) \
          .filter(AgentTypeAttribute.name == 'char_mass').all():
            if agent.AgentType.name == agent_name:
                value = float(agent.AgentTypeAttribute.value)
    value = value * agent_quantity
    total = {'mass': value}
    return json.dumps(total)


@app.route('/get_energy', methods=['GET'])
def get_energy():
    """
    Sends front end energy values for config wizard.
    Takes in the request values 'agent_name' and 'quantity'

    Returns
    -------
    json object with energy value for agent
    """

    agent_name = request.args.get('agent_name', type=str)
    agent_quantity = request.args.get('quantity', 1, type=int) or 1
    agent_desc = load_from_basedir('data_files/agent_desc.json')
    total = {}
    if agent_name == 'solar_pv_array_mars':
        value_type = 'energy_output'
        data = agent_desc['power_generation'][agent_name]
        total_kwh = next((float(e['value'])
                          for e in data['data']['output']
                          if e['type'] == 'kwh'), 0)
    elif agent_name == 'power_storage':
        value_type = 'energy_capacity'
        data = agent_desc['storage']['power_storage']
        total_kwh = next((float(e['value'])
                          for e in data['data']['characteristics']
                          if e['type'] == 'capacity_kwh'), 0)
    else:
        value_type = 'energy_input'
        total_kwh = 0
        for agent_class, agents in agent_desc.items():
            for name, data in agents.items():
                if (agent_name == 'eclss' == agent_class or
                    agent_name == name):
                    total_kwh += next((float(e['value'])
                                       for e in data['data']['input']
                                       if e['type'] == 'kwh'), 0)
    value = total_kwh * agent_quantity
    total = {value_type : value}
    return json.dumps(total)


def calc_air_storage(volume):
    # 1 m3 of air weighs ~1.25 kg (depending on temperature and humidity)
    AIR_DENSITY = 1.25  # kg/m3
    # convert from m3 to kg
    mass = volume * AIR_DENSITY
    # atmosphere component breakdown (see PRD)
    percentages = {
        "n2": 78.084,  # nitrogen
        "o2": 20.946,  # oxygen
        "co2": 0.041332,  # carbon dioxide
        "ch4": 0.000187,  # methane
        "h2": 0.000055,  # hydrogen
        "h2o": 1,  # water vapor
        # the followings are not included
        #"atmo_ar": 0.9340,  # argon
        #"atmo_ne": 0.001818,  # neon
        #"atmo_he": 0.000524,  # helium
        #"atmo_kr": 0.000114,  # krypton
    }
    # calculate the mass for each element
    return dict({label: mass*perc/100 for label, perc in percentages.items()},
                total_capacity=dict(value=mass, unit='kg'))


def calc_water_storage(volume):
    # the total_capacity is in kg, and it's equal to the volume'
    return dict({'potable': 0.9 * volume, 'treated': 0.1 * volume},
                total_capacity=dict(value=volume, unit='kg'))


def build_connections_from_agent_desc(fpath):
    """Build agent_conn.json file from the current agent_desc.json file.

    DEPRECATED 19 October:
      - co2_removal_SAWD and co2_makeup_valve connect to co2_storage

    """
    agent_desc_path = pathlib.Path(__file__).parent.parent / 'data_files/agent_desc.json'
    with open(agent_desc_path) as f:
        agent_desc = json.load(f)

    currencies = agent_desc['simulation_variables']['currencies_of_exchange']
    currency_dict = {}
    for c in currencies:
        group = c.split("_")[0]
        if group == 'atmo':
            currency_dict[c] = 'habitat'
        elif group in 'sold':
            currency_dict[c] = 'nutrient_storage'
        elif group == 'food':
            currency_dict[c] = 'food_storage'
        elif group == 'h2o':
            currency_dict[c] = 'water_storage'
        elif group == 'enrg':
            currency_dict[c] = 'power_storage'
    currency_dict['biomass_totl'] = 'nutrient_storage' # This one is odd

    arrows = []
    for agent_class, agents in agent_desc.items():
        if agent_class in {'simulation_variables', 'storage'}:
            continue
        for agent in agents:
            data = agents[agent]['data']
            for prefix in ['input', 'output']:
                for flow in data[prefix]:
                    c = flow['type']
                    if c not in currency_dict:
                        print(f"{c!r} not in currency_dict.")
                        continue
                    internal_conn = f"{agent}.{c}"
                    external_conn = f"{currency_dict[c]}.{c}"
                    if prefix == 'input':
                        arrows.append({'from': external_conn,
                                       'to': internal_conn})
                    elif prefix == 'output':
                        arrows.append({'from': internal_conn,
                                       'to': external_conn})

    with open(fpath, 'w') as f:
        agent_desc = json.dump(arrows, f)
    return arrows

def convert_configuration(game_config, agent_desc=None, save_output=False):
    """
    This method converts the json configuration from a post into a more complete configuration
    with connections.

    GRANT: This file is undergoing a major change as of October '21.
      - In the first step, I load connections programmatically from
        'agent_conn.json', and do some reorganization to make the function
        easier to read.
      - Next, I remove the distinction between Agent and Storage.
      - I allow for new, user-defined agents to be parsed using the same methodology
    """
    full_game_config = {  # The object to be returned by this function.
        'agents': {},
        'termination': [],
    }
    # Create a working_config which will be modified by this function, so as
    # not to modify the original.
    working_config = copy.deepcopy(game_config)

    # Load the agent_desc to validate agents in config and get structure volume
    # November '22: This was formerly done by the database.
    if agent_desc is None:
        agent_desc = load_from_basedir('data_files/agent_desc.json')

    ###########################################################################
    #                   STEP 1: Add non-agent fields                          #
    ###########################################################################

    # Determines if multi-instance agents are independent agents or a group
    if 'single_agent' in working_config:
        single_agent = working_config.pop('single_agent')
    else:
        single_agent = 0
    full_game_config['single_agent'] = single_agent
    # Sets the length of the simulation
    if 'duration' in working_config and isinstance(working_config['duration'], dict):
        duration = working_config.pop('duration')
        full_game_config['termination'].append({
            'condition': 'time',
            'value': duration.get('value', 0) or 0,
            'unit': duration.get('type', 'day')})
    # Optional fields
    for label in ['priorities', 'minutes_per_step', 'location']:
        if label in working_config and isinstance(working_config[label], dict):
            full_game_config[label] = working_config.pop(label)
    # Structures MUST step before other agents so that the `.._ratio` fields
    # are availble for threshold tests.
    if 'priorities' not in full_game_config:
        full_game_config['priorities'] = ['structures', 'storage', 'power_generation',
                                          'inhabitants', 'eclss', 'plants']

    ###########################################################################
    #             STEP 2: Flatten the working_config object                   #
    ###########################################################################
    # The game_config object sent by the frontend has some irregularities. In
    # order to accomodate user-created agents in the future, we first flatten
    # items that are known to be irregular, add some custom information, and
    # then add everything in working_config, validating based on whether
    # they're in the database.

    # Structures: A string under 'habitat' and 'greenhouse' with selected type.
    structures_dict = {}  # Used to replace generic connections
    total_volume = 0  # Used to calcualte starting water_storage
    if 'habitat' in working_config or 'greenhouse' in working_config:
        valid_structures = list(agent_desc['structures'].keys())
        for structure in ['habitat', 'greenhouse']:
            if structure not in working_config or not isinstance(working_config[structure], str):
                continue
            structure_type = working_config.pop(structure)
            if structure_type not in valid_structures:
                continue
            structures_dict[structure] = structure_type
            volume = next((
                char['value'] for char in
                agent_desc['structures'][structure_type]['data']['characteristics']
                if char['type'] == 'volume'), 0)
            total_volume += volume  # Used below to calculate starting water
            atmosphere = calc_air_storage(volume)  # Fill with earth-normal atmosphere
            working_config[structure_type] = dict(id=1, amount=1, **atmosphere)
    if 'habitat' in structures_dict and 'greenhouse' in structures_dict:
        working_config['atmosphere_equalizer'] = dict(id=1, amount=1)
    # With plant growth update, a light agent is required
    working_config['light'] = dict(amount=1)
    # Default Storages: Some listed, some not. Need to calculate amount.
    # 'food_storage' now holds fresh food, and 'ration_storage' holds the rations. Rations are
    # still pre-loaded to 'food_storage' on the front-end though, so need to change the label.
    if 'food_storage' in working_config:
        storage = working_config.pop('food_storage')
        working_config['ration_storage'] = storage
    for storage_type in ['water_storage', 'nutrient_storage', 'ration_storage', 'power_storage']:
        if storage_type in working_config and isinstance(working_config[storage_type], dict):
            storage = working_config.pop(storage_type)
        else:
            storage = {}
        # Preload water based on habitat & greenhouse volume
        if storage_type == 'water_storage' and total_volume:
            storage = dict(**storage, **calc_water_storage(total_volume))
        # Determine storage amount based on capacity and starting balance
        if 'amount' in storage and isinstance(storage['amount'], int):
            amount = max(1, storage.pop('amount'))
        else:
            amount = 1
        storage_desc = agent_desc['storage'][storage_type]
        for char in storage_desc['data']['characteristics']:
            if char['type'].startswith('capacity'):
                currency = char['type'].split('_', 1)[1]
                if currency not in storage:
                    storage[currency] = 0
                capacity = int(char['value'])
                amount = max(amount, math.ceil(storage[currency] / capacity))
        working_config[storage_type] = dict(id=1, amount=amount, **storage)
    # ECLSS: A single item with an amount; needs to be broken into component agents
    eclss_agents = ['solid_waste_aerobic_bioreactor', 'multifiltration_purifier_post_treatment',
                    'oxygen_generation_SFWE', 'urine_recycling_processor_VCD', 'co2_removal_SAWD',
                    'co2_makeup_valve', 'co2_storage', 'co2_reduction_sabatier',
                    'ch4_removal_agent', 'dehumidifier']
    if 'eclss' in working_config and isinstance(working_config['eclss'], dict):
        eclss = working_config.pop('eclss')
        amount = eclss.get('amount', 0) or 0
        if amount:
            for eclss_agent in eclss_agents:
                this_amount = amount
                if eclss_agent in {'co2_makeup_valve', 'dehumidifier',
                                   'multifiltration_purifier_post_treatment'}:
                    # With the updated plant growth model, extra capacity is
                    # needed for these 3 agents in order to run successfully.
                    this_amount *= 3
                working_config[eclss_agent] = dict(id=1, amount=this_amount)
                if eclss_agent == 'co2_storage':
                    # With update, a higher CO2 concentration is maintained
                    # and supplemental CO2 is required to keep it there
                    working_config[eclss_agent]['co2'] = 200
    # Plants: A list of objects with 'species' and 'amount'
    plants_in_config = []
    if 'plants' in working_config and isinstance(working_config['plants'], list):
        plants = working_config.pop('plants')
        for plant in plants:
            if isinstance(plant, dict):
                amount = plant.get('amount', 0) or 0
                plant_type = plant.get('species', None)
                if plant_type and amount:
                    plants_in_config.append(plant_type)
                    working_config[plant_type] = dict(amount=amount)
    if len(plants_in_config) > 0:
        food_storage = {}
        food_storage_desc = agent_desc['storage']['food_storage']
        for char in food_storage_desc['data']['characteristics']:
            if char['type'].startswith('capacity'):
                currency = char['type'].split('_', 1)[1]
                if currency in plants_in_config:
                    food_storage[currency] = 0
        if len(food_storage.keys()) > 0:
            working_config['food_storage'] = dict(id=1, amount=1, **food_storage)
    # 'human_agent' and 'solar_pv...' are already in the correct format.

    ###########################################################################
    #                   STEP 3: Add all agents to output                      #
    ###########################################################################

    valid_agents = set()
    for agents in agent_desc.values():
        for agent in agents:
            valid_agents.add(agent)
    for agent_type, attrs in working_config.items():
        if not isinstance(attrs, dict):
            print(f"Attributes for agent type {agent_type} must be a dict")
            continue
        if agent_type not in valid_agents:
            print(f"Agent type {agent_type} not found in agent_desc")
            continue
        full_game_config['agents'][agent_type] = attrs
    # Calculate the total number of agents. Used in `views.py` to enforce a
    # maximum number of agents per simulation (currently 50).
    if single_agent:
        full_game_config['total_amount'] = len(full_game_config['agents'])
    else:
        full_game_config['total_amount'] = \
            sum([agent.get('amount', 1) for agent in full_game_config['agents']])

    # Print result
    if save_output:
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime("%m%d%H%M%S")
        with open(f"full_game_config_{timestamp}.json", "w") as f:
            json.dump(full_game_config, f)

    return full_game_config


def calc_step_per_agent(step_record_data, output, agent_types=(), currency_types=(), directions=(),
                        value_round=6):
    for step in step_record_data:
        direction = step['direction']
        agent_type = step['agent_type']
        currency_type = step['currency_type']
        if agent_types and agent_type not in agent_types:
            continue
        elif currency_types and currency_type not in currency_types:
            continue
        elif directions and direction not in directions:
            continue
        else:
            output[direction][currency_type][agent_type]['value'] = \
                round(output[direction][currency_type][agent_type]['value'] + step['value'],
                      value_round)
            output[direction][currency_type][agent_type]['unit'] = step['unit']
    return output


def calc_step_in_out(direction, currencies, step_record_data, value_round=6):
    """
    Calculate the total production or total consumption of given currencies for a given step.

    Called from: route views.get_step()

    Input: direction 'in' or 'out' in=consumption, out=production
    currencies = list of currencies for which to calculate consumption or production. e.g.
    currencies = ['atmo_o2',''engr_kwh'] step_record_data = StepRecord for this step_num

    Output: dictionary of values and units for each currency. e.g. {'atmo_o2': {'value': 0.05,
    'units': 'kg'}}. The unit is selected from the first currency, assuming all currencies with this
    name have the same units.
    """

    output = {}
    for currency in currencies:
        output[currency] = {'value': 0, 'unit': ''}

    for step in step_record_data:
        currency = step['currency_type']
        if step['direction'] == direction and currency in output:
            output[currency]['value'] = round(output[currency]['value'] + step['value'], value_round)
            output[currency]['unit'] = step['unit']

    return output


def calc_step_storage_ratios(agents, model_record_data, value_round=6):
    """
    Calculate the ratio for the requested currencies for the requested <agent_type>_<agent_id>.

    Called from: route views.get_step()

    Input: agents = dictionary of agents for which to calculate ratios. For each agent, give a list
    of the currencies which should be included in the output. e.g. {'air_storage_1': ['atmo_co2']}.
    step_record_data = StepRecord for this step_num.

    Output: dictionary of agents, each agent has a dictionary of currency:ratio pairs. e.g.
    {'air_storage_1': {'atmo_co2': 0.21001018914835098}
    """

    user_id = model_record_data['user_id']
    game_id = model_record_data['game_id']
    step_num = model_record_data['step_num']
    storage_capacities = redis_conn.lrange(f'storage_capacities:{user_id}:{game_id}:{step_num}', 0, -1)
    storage_capacities = map(json.loads, storage_capacities)

    output = {}
    for agent in agents:
        agent_type = agent[:agent.rfind('_')]
        agent_id = int(agent[agent.rfind('_')+1:])
        agent_capacities = [record for record in storage_capacities
                            if record['storage_type'] == agent_type
                            and record['storage_id'] == agent_id]

        # First, get sum of all currencies
        total_value = 0
        unit = ''
        for record in agent_capacities:
            total_value += record['value']
            if unit == '':
                unit = record['unit']
            else:
                if not record['unit'] == unit:
                    sys.exit('ERROR in front_end_routes.calc_step_storage_ratios().'
                             'Currencies do not have same units.', unit, record['unit'])

        output[agent] = {}
        # Now, calculate the ratio for specified currencies.
        for currency in agents[agent]:
            c_step_data = [record for record in agent_capacities
                           if record['currency_type'] == currency][0]
            output[agent][currency] = round(c_step_data['value'] / total_value, value_round)

    return output


def count_agents_in_step(agent_types, model_record_data):
    """
    Count the number of agents matching the agent_name for this step

    Called from: route views.get_step()

    Input: agent_names, step_record_data

    Output: dictionary of counts for each agent names {'human_agent': count}
    """

    output = {}
    for agent_type in agent_types:
        output[agent_type] = 0

    user_id = model_record_data['user_id']
    game_id = model_record_data['game_id']
    step_num = model_record_data['step_num']
    agent_type_counts = redis_conn.lrange(f'agent_type_counts:{user_id}:{game_id}:{step_num}', 0, -1)
    agent_type_counts = map(json.loads, agent_type_counts)
    for record in agent_type_counts:
        if record['agent_type'] in output:
            output[record['agent_type']] += record['agent_counter']

    return output


def sum_agent_values_in_step(agent_types, currency_type_name, direction, step_record_data):
    """
    Sum the values for this agent

    Called from: route views.get_step()

    Input: agent_names, step_record_data

    Output: dictionary of sum of values and units for each agent names {'rice':{'value': value,
    'unit': unit}}
    """

    output = {}
    for agent_type in agent_types:
        output[agent_type] = {'value': 0, 'unit': ''}

    for step in step_record_data:
        agent_type = step.agent_type.name
        if (step.currency_type.name == currency_type_name
                and step.direction == direction and agent_type in output):
            output[agent_type]['value'] += step.value
            output[agent_type]['unit'] = step.unit

    return output


def calc_step_storage_capacities(agent_types, model_record_data, value_round=6):
    output = {}
    user_id = model_record_data['user_id']
    game_id = model_record_data['game_id']
    step_num = model_record_data['step_num']
    storage_capacities = redis_conn.lrange(f'storage_capacities:{user_id}:{game_id}:{step_num}', 0, -1)
    storage_capacities = map(json.loads, storage_capacities)
    for record in storage_capacities:
        agent_type = record['storage_type']
        storage_id = record['storage_id']
        currency = record['currency_type']
        if (len(agent_types) == 0 or
           (agent_type in agent_types and
            (currency in agent_types[agent_type] or
             len(agent_types[agent_type]) == 0))):
            if agent_type not in output:
                output[agent_type] = {}
            if storage_id not in output[agent_type]:
                output[agent_type][storage_id] = {}
            output[agent_type][storage_id][currency] = {'value': round(record['value'], value_round),
                                                        'unit': record['unit']}
    return output


def get_growth_rates(agent_types, step_record_data):
    output = {}
    for agent_type in agent_types:
        output[agent_type] = None
    for step in step_record_data:
        agent_type = step['agent_type']
        if agent_type in output and step['growth']:
            if not output[agent_type] or step['growth'] > output[agent_type]:
                output[agent_type] = step['growth']
    return output


def load_from_basedir(fname):
    basedir = pathlib.Path(app.root_path).resolve().parent
    path = basedir / fname
    result = {}
    try:
        with path.open() as f:
            result = json.load(f)
    except OSError as e:
        app.logger.exception(f'Error opening {fname}: {e}')
    except ValueError as e:
        app.logger.exception(f'Error reading {fname}: {e}')
    except Exception as e:
        app.logger.exception(f'Unexpected error handling {fname}: {e}')
    finally:
        return result
