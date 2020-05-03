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


def calc_air_storage(volume):
    # 1 m3 of air weighs ~1.25 kg (depending on temperature and humidity)
    AIR_DENSITY = 1.25  # kg/m3
    # convert from m3 to kg
    mass = volume * AIR_DENSITY
    # atmosphere component breakdown (see PRD)
    percentages = {
        "atmo_n2": 78.084,  # nitrogen
        "atmo_o2": 20.946,  # oxygen
        "atmo_co2": 0.041332,  # carbon dioxide
        "atmo_ch4": 0.000187,  # methane
        "atmo_h2": 0.000055,  # hydrogen
        "atmo_h2o": 1,  # water vapor
        # the followings are not included
        #"atmo_ar": 0.9340,  # argon
        #"atmo_ne": 0.001818,  # neon
        #"atmo_he": 0.000524,  # helium
        #"atmo_kr": 0.000114,  # krypton
    }
    # calculate the mass for each element
    return {label: mass*perc/100 for label, perc in percentages.items()}


def calc_water_storage(volume):
    return {'h2o_potb': 0.9 * volume, 'h2o_tret': 0.1 * volume}


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
    total_amount = 0

    # Anything in this list will be copied as is from the input to the full_game_config. If it's not
    # in the input it will be ignored
    labels_to_direct_copy = ['priorities', 'minutes_per_step', 'location']

    manual_entries = ['habitat', 'greenhouse']

    # Is it a single agent
    single_agent = game_config.get('single_agent', 0) or 0

    if 'habitat' in game_config or 'greenhouse' in game_config:
        total_volume = 0
        structures = db.session.query(AgentType).filter_by(agent_class='structures').all()
        structures = [agent.name for agent in structures]
        for structure in ['habitat', 'greenhouse']:
            if game_config.get(structure) not in structures:
                continue  # invalid structure or none
            if structure in game_config:
                agent_type, type_attribute = db.session.query(AgentType, AgentTypeAttribute) \
                    .filter_by(name=game_config[structure]) \
                    .filter(AgentType.id == AgentTypeAttribute.agent_type_id) \
                    .filter(AgentTypeAttribute.name == 'char_volume').first()
                total_volume += float(type_attribute.value)

        def _update_config(game_config, storage_type, data):
            if storage_type not in game_config:
                game_config[storage_type] = data
            else:
                for k, v in data.items():
                    game_config[storage_type][k] = game_config[storage_type].get(k, 0) + v
            return game_config

        game_config = _update_config(game_config, 'air_storage', calc_air_storage(total_volume))
        game_config = _update_config(game_config, 'water_storage', calc_water_storage(total_volume))

    eclss_amount = 0
    if 'eclss' in game_config and isinstance(game_config['eclss'], dict):
        eclss_amount = game_config['eclss'].get('amount', 0) or 0
        total_amount += 6 if single_agent else (eclss_amount * 6)

    human_amount = 0
    if 'human_agent' in game_config and isinstance(game_config['human_agent'], dict):
        human_amount = game_config['human_agent'].get('amount', 0) or 0
        total_amount += 1 if single_agent else human_amount

    # Any agents with power_storage or food_storage will be assined power_storage = power
    # connections (defined later) etc. Agents initialised here must have all connections named here.
    full_game_config = {'agents': {'human_agent': [{'connections': {'air_storage': [],
                                                                    'water_storage': [],
                                                                    'food_storage': []},
                                                    'amount': human_amount}],
                                   'solid_waste_aerobic_bioreactor': [{'connections': {'air_storage': [],
                                                                                       'power_storage': [],
                                                                                       'water_storage': [],
                                                                                       'nutrient_storage': []},
                                                                       'amount': eclss_amount}],
                                   'multifiltration_purifier_post_treatment': [{'connections': {'water_storage': [],
                                                                                                'power_storage': []},
                                                                               'amount': eclss_amount}],
                                   'oxygen_generation_SFWE': [{'connections': {'air_storage': [],
                                                                               'power_storage': [],
                                                                               'water_storage': []},
                                                               'amount': eclss_amount}],
                                   'urine_recycling_processor_VCD': [{'connections': {'power_storage': [],
                                                                                      'water_storage': [],
                                                                                      'nutrient_storage': []},
                                                                      'amount': eclss_amount}],
                                   'co2_removal_SAWD': [{'connections': {'air_storage': [],
                                                                         'power_storage': []},
                                                         'amount': eclss_amount}],
                                   'co2_reduction_sabatier': [{'connections': {'air_storage': [],
                                                                               'power_storage': [],
                                                                               'water_storage': []},
                                                               'amount': eclss_amount}],
                                   'dehumidifier': [{'connections': {'air_storage': [],
                                                                     'power_storage': [],
                                                                     'water_storage': []},
                                                     'amount': eclss_amount}],
                                   },
                        'storages': {'air_storage': [],
                                     'water_storage': [],
                                     'nutrient_storage': [],
                                     'power_storage': [],
                                     'food_storage': []},
                        'termination': [],
                        'single_agent': single_agent
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

    # The rest of this function is for reformatting agents. Food_connections and power_connections
    # will be assigned to all agents with food_storage or power_storage respectively, at the end of
    # this function.
    connections = {}
    for storage_type in ['air_storage', 'water_storage', 'nutrient_storage', 'food_storage',
                         'power_storage']:
        storage = {}
        minimum_storage_amount = 0
        agent_type = AgentType.query.filter_by(name=storage_type).first()
        for attr in agent_type.agent_type_attributes:
            if attr.name.startswith('char_capacity'):
                storage_capacity = int(attr.value)
                currency = attr.name.split('_', 2)[2]
                if storage_type in game_config:
                    storage[currency] = game_config[storage_type].get(currency, 0) or 0
                    minimum_storage_amount = max(minimum_storage_amount, 1)
                else:
                    storage[currency] = 0
                minimum_storage_amount = max(minimum_storage_amount,
                                             math.ceil(storage[currency] / storage_capacity))
        if storage_type not in connections:
            connections[storage_type] = []
        for i in range(minimum_storage_amount):
            x = len(connections[storage_type]) + 1
            connections[storage_type].append(x)
            full_game_config['storages'][storage_type] \
                .append({'id': x, **{k: v / minimum_storage_amount for k, v in storage.items()}})

    for label in manual_entries:
        if label in game_config:
            full_game_config['agents'][game_config[label]] = [{'connections': {'air_storage': [],
                                                                               'water_storage': [],
                                                                               'nutrient_storage': [],
                                                                               'power_storage': [],
                                                                               'food_storage': []},
                                                               'amount': 1}]

    pv_arrays = ['solar_pv_array_mars', 'solar_pv_array_moon']
    for agent_type in pv_arrays:
        if agent_type in game_config and isinstance(game_config[agent_type], dict):
            amount = game_config[agent_type].get('amount', 0) or 0
            total_amount += 1 if single_agent else amount
            full_game_config['agents'][agent_type] = [{'connections': {'power_storage': []},
                                                       'amount': amount}]

    # If the front_end specifies an amount for this agent, overwrite any default values with the
    # specified value
    for x, y in full_game_config['agents'].items():
        if x in game_config and isinstance(game_config[x], dict):
            y[0]['amount'] = game_config[x].get('amount', 0) or 0
            total_amount += 1 if single_agent else y[0]['amount']

    # Plants are treated separately because its a list of items which must be assigned as agents
    if 'plants' in game_config and isinstance(game_config['plants'], list):
        for plant in game_config['plants']:
            if isinstance(plant, dict):
                amount = plant.get('amount', 0) or 0
                agent_type = plant.get('species', None)
                total_amount += 1 if single_agent else amount
                if agent_type:
                    full_game_config['agents'][agent_type] = [{'connections': {'air_storage': [],
                                                                               'water_storage': [],
                                                                               'nutrient_storage': [],
                                                                               'power_storage': [],
                                                                               'food_storage': []},
                                                               'amount': amount}]

    for agent in full_game_config['agents'].values():
        for storage_type in connections:
            if storage_type in agent[0]['connections']:
                agent[0]['connections'][storage_type] = connections[storage_type]

    full_game_config['total_amount'] = total_amount

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
