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
    agent_quantity = request.args.get('quantity', type=int)
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
    agent_quantity = request.args.get('quantity', type=int)
    attribute_name = 'in_enrg_kwh'
    value_type = 'energy_input'
    total = {}
    if agent_name == 'eclss':
        total_eclss = 0
        for agent in db.session.query(AgentType, AgentTypeAttribute) \
          .filter(AgentType.id == AgentTypeAttribute.agent_type_id) \
          .filter(AgentTypeAttribute.name == 'in_enrg_kwh') \
          .filter(AgentType.agent_class == 'eclss').all():
            total_eclss += float(agent.AgentTypeAttribute.value)
        value = total_eclss * agent_quantity
        total = {value_type : value}
    else:
        if agent_name == 'solar_pv_array_mars':
            attribute_name = 'out_enrg_kwh'
            value_type = 'energy_output'
        elif agent_name == 'power_storage':
            attribute_name = 'char_capacity_enrg_kwh'
            value_type = 'energy_capacity'
        for agent in db.session.query(AgentType, AgentTypeAttribute) \
          .filter(AgentType.id == AgentTypeAttribute.agent_type_id) \
          .filter(AgentTypeAttribute.name == attribute_name).all():
            if agent.AgentType.name == agent_name:
                value = float(agent.AgentTypeAttribute.value) * agent_quantity
                total = { value_type : value}
    return json.dumps(total)


def convert_configuration(game_config):
    """
    This method converts the json configuration from a post into a more complete configuration
    with connections.

    THOMAS: This was created to allow the front end to send over a simplified version without
    connections. Connections are actually set up to connect to everything automatically, so this
    could use a re-haul. It also has some atmosphere values that are hard coded here that should be
    defined either in the agent library or sent from the front end. If this route is kept, most of
    the functionality should be moved into a separate object to help declutter and keep a solid
    separation of concerns. If it is removed, the data from the front end needs to be changed into a
    format based on an object similar to the one created here or in the new game view.
    """

    # Anything in this list will be copied as is from the input to the full_game_config. If it's not
    # in the input it will be ignored
    labels_to_direct_copy = ['priorities', 'minutes_per_step', 'location']

    manual_entries = ['habitat', 'greenhouse']

    eclss_amount = 0
    if 'eclss' in game_config and isinstance(game_config['eclss'], dict):
        eclss_amount = game_config['eclss'].get('amount', 0) or 0

    human_amount = 0
    if 'human_agent' in game_config and isinstance(game_config['human_agent'], dict):
        human_amount = game_config['human_agent'].get('amount', 0) or 0

    # Any agents with power_storage or food_storage will be assined power_storage = power
    # connections (defined later) etc. Agents initialised here must have all connections named here.
    full_game_config = {'agents': {'human_agent': [{'connections': {'air_storage': [1],
                                                                    'water_storage': [1],
                                                                    'food_storage': []},
                                                    'amount': human_amount}],
                                   'solid_waste_aerobic_bioreactor': [{'connections': {'air_storage': [1],
                                                                                       'power_storage': [],
                                                                                       'water_storage': [1],
                                                                                       'nutrient_storage': [1]},
                                                                       'amount': eclss_amount}],
                                   'multifiltration_purifier_post_treament': [{'connections': {'water_storage': [1],
                                                                                               'power_storage': [1]},
                                                                               'amount': eclss_amount}],
                                   'oxygen_generation_SFWE': [{'connections': {'air_storage': [1],
                                                                               'power_storage': [],
                                                                               'water_storage': [1]},
                                                               'amount': eclss_amount}],
                                   'urine_recycling_processor_VCD': [{'connections': {'power_storage': [],
                                                                                      'water_storage': [1]},
                                                                      'amount': eclss_amount}],
                                   'co2_removal_SAWD': [{'connections': {'air_storage': [1],
                                                                         'power_storage': []},
                                                         'amount': eclss_amount}],
                                   'co2_reduction_sabatier': [{'connections': {'air_storage': [1],
                                                                               'power_storage': [],
                                                                               'water_storage': [1]},
                                                               'amount': eclss_amount}]
                                   },
                        'storages': {'air_storage': [{'id': 1,
                                                      'atmo_h2o': 10,
                                                      'atmo_o2': 2100,
                                                      'atmo_co2': 3.5,
                                                      'atmo_n2': 7886,
                                                      'atmo_ch4': 0.009531,
                                                      'atmo_h2': 0.005295}],
                                     'water_storage': [{'id': 1,
                                                        'h2o_potb': 9000,
                                                        'h2o_tret': 1000,
                                                        'h2o_wste': 0,
                                                        'h2o_urin': 0}],
                                     'nutrient_storage': [{'id': 1,
                                                           'sold_n': 100,
                                                           'sold_p': 100,
                                                           'sold_k': 100}],
                                     'power_storage': [],
                                     'food_storage': []},
                        'termination': []
                        }

    # This is where labels from labels_to_direct_copy are copied directly from game_config to full
    # game_config
    for label in labels_to_direct_copy:
        if label in game_config:
            full_game_config[label] = game_config[label]

    # Assign termination values
    if 'duration' in game_config and isinstance(game_config['duration'], dict):
        duration = {'condition': 'time',
                    'value': game_config['duration'].get('value', 0) or 0,
                    'unit': game_config['duration'].get('type', 'day')}
        full_game_config['termination'].append(duration)

    # Is it a single agent
    full_game_config['single_agent'] = game_config.get('single_agent', 0) or 0

    # The rest of this function is for reformatting agents. Food_connections and power_connections
    # will be assigned to all agents with food_storage or power_storage respecitively, at the end of
    # this function.

    food_connections = []
    if 'food_storage' in game_config and isinstance(game_config['food_storage'], dict):
        food_storage_capacity = int(db.session.query(AgentType, AgentTypeAttribute)
                                    .filter(AgentType.id == AgentTypeAttribute.agent_type_id)
                                    .filter(AgentTypeAttribute.name == 'char_capacity_food_edbl')
                                    .first().AgentTypeAttribute.value)
        food_left = game_config['food_storage'].get('amount', 0) or 0
        food_storage_amount = math.ceil(food_left / food_storage_capacity)
        for x in range(1, int(food_storage_amount) + 1):
            food_connections.append(x)
            if food_left > food_storage_capacity:
                full_game_config['storages']['food_storage'] \
                  .append({'id': x,'food_edbl': food_storage_capacity})
                food_left -= food_storage_capacity
            else:
                full_game_config['storages']['food_storage'].append({'id': x,
                                                                     'food_edbl': food_left})

    power_connections = []
    if 'power_storage' in game_config and isinstance(game_config['power_storage'], dict):
        power_storage_capacity = int(db.session.query(AgentType, AgentTypeAttribute)
                                     .filter(AgentType.id == AgentTypeAttribute.agent_type_id)
                                     .filter(AgentTypeAttribute.name == 'char_capacity_enrg_kwh')
                                     .first().AgentTypeAttribute.value)
        power_left = game_config['power_storage'].get('amount', 0) or 0
        power_storage_amount = math.ceil(power_left / power_storage_capacity)
        for x in range(1, int(power_storage_amount) + 1):
            power_connections.append(x)
            if power_left > power_storage_capacity:
                full_game_config['storages']['power_storage'] \
                  .append({'id': x,'enrg_kwh': power_storage_capacity})
                power_left -= power_storage_capacity
            else:
                full_game_config['storages']['power_storage'].append({'id': x,
                                                                      'enrg_kwh': power_left})

    for label in manual_entries:
        if label in game_config:
            full_game_config['agents'][game_config[label]] = [{'connections': {'air_storage': [1],
                                                                               'water_storage': [1],
                                                                               'nutrient_storage': [1],
                                                                               'power_storage': [],
                                                                               'food_storage': []},
                                                               'amount': 1}]

    pv_arrays = ['solar_pv_array_mars', 'solar_pv_array_moon']
    for agent_type in pv_arrays:
        if agent_type in game_config and isinstance(game_config[agent_type], dict):
            amount = game_config[agent_type].get('amount', 0) or 0
            full_game_config['agents'][agent_type] = [{'connections': {'power_storage': []},
                                                       'amount': amount}]

    # If the front_end specifies an amount for this agent, overwrite any default values with the
    # specified value
    for x, y in full_game_config['agents'].items():
        if x in game_config and isinstance(game_config[x], dict):
            y[0]['amount'] = game_config[x].get('amount', 0) or 0

    # Plants are treated separately because its a list of items which must be assigned as agents
    if 'plants' in game_config and isinstance(game_config['plants'], list):
        for plant in game_config['plants']:
            if isinstance(plant, dict):
                amount = plant.get('amount', 0) or 0
                agent_type = plant.get('species', None)
                if agent_type:
                    full_game_config['agents'][agent_type] = [{'connections': {'air_storage': [1],
                                                                               'water_storage': [1],
                                                                               'nutrient_storage': [1],
                                                                               'power_storage': [],
                                                                               'food_storage': []},
                                                               'amount': amount}]

    # Here, power connections and food connections are assigned to all agents with power_storage or
    # food_storage specified.
    for agent in full_game_config['agents'].values():
        if 'power_storage' in agent[0]['connections']:
            agent[0]['connections']['power_storage'] = power_connections
        if 'food_storage' in agent[0]['connections']:
            agent[0]['connections']['food_storage'] = food_connections

    return full_game_config


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
    storage_capacities = [json.loads(r) for r in storage_capacities]

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
    agent_type_counts = [json.loads(r) for r in agent_type_counts]
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
    storage_capacities = [json.loads(r) for r in storage_capacities]
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
