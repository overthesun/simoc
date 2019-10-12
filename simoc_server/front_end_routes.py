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

from simoc_server import app, db
from simoc_server.database.db_model import AgentType, AgentTypeAttribute, StorageCapacityRecord, \
    AgentTypeCountRecord


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

    # If a game_config element should be assigned as an agent with connections: power_storage only,
    # add it to the list below (unless you want to rename the agent, then it will need it's own
    # code) Note, this assumes power_storage is the only connection for this agent. Do not add
    # agents which have other connections. Only agents which are present in the input game_config
    # will be assigned
    agents_to_assign_power_storage = ['habitat', 'greenhouse']

    eclss_amount = game_config['eclss'].get('amount', 0) if 'eclss' in game_config else 0

    # Any agents with power_storage or food_storage will be assined power_storage = power
    # connections (defined later) etc. Agents initialised here must have all connections named here.
    full_game_config = {'agents': {'human_agent': [{'connections': {'air_storage': [1],
                                                                    'water_storage': [1],
                                                                    'food_storage': []}}],
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
    if 'duration' in game_config:
        duration = {'condition': 'time',
                    'value': game_config['duration'].get('value', 0),
                    'unit': game_config['duration'].get('type', 'day')}
        full_game_config['termination'].append(duration)

    # Is it a single agent
    full_game_config['single_agent'] = game_config.get('single_agent', 0)

    # The rest of this function is for reformatting agents. Food_connections and power_connections
    # will be assigned to all agents with food_storage or power_storage respecitively, at the end of
    # this function.

    # Determine the food and power connections to be assigned to all agents with food and power
    # storage later
    food_storage_capacity = int(db.session.query(AgentType, AgentTypeAttribute)
                                .filter(AgentType.id == AgentTypeAttribute.agent_type_id)
                                .filter(AgentTypeAttribute.name == 'char_capacity_food_edbl')
                                .first().AgentTypeAttribute.value)
    food_amount = game_config['food_storage'].get('amount', 0)
    food_storage_amount = math.ceil(food_amount / food_storage_capacity)

    food_connections = []
    food_left = food_amount
    for x in range(1, int(food_storage_amount) + 1):
        food_connections.append(x)
        if food_left > food_storage_capacity:
            full_game_config['storages']['food_storage'] \
              .append({'id': x,'food_edbl': food_storage_capacity})
            food_left -= food_storage_capacity
        else:
            full_game_config['storages']['food_storage'].append({'id': x, 'food_edbl': food_left})

    power_storage_capacity = int(db.session.query(AgentType, AgentTypeAttribute)
                                 .filter(AgentType.id == AgentTypeAttribute.agent_type_id)
                                 .filter(AgentTypeAttribute.name == 'char_capacity_enrg_kwh')
                                 .first().AgentTypeAttribute.value)
    power_amount = game_config['power_storage'].get('amount', 0)
    power_storage_amount = math.ceil(power_amount / power_storage_capacity)

    power_connections = []
    power_left = power_amount
    for x in range(1, int(power_storage_amount) + 1):
        power_connections.append(x)
        if power_left > power_storage_capacity:
            full_game_config['storages']['power_storage'] \
              .append({'id': x,'enrg_kwh': power_storage_capacity})
            power_left -= power_storage_capacity
        else:
            full_game_config['storages']['power_storage'].append({'id': x, 'enrg_kwh': power_left})

    # Here, agents from agents_to_assign_power_storage are assigned with only a power_storage
    # connection.
    for labelps in agents_to_assign_power_storage:
        if labelps in game_config:
            full_game_config['agents'][game_config[labelps]] = [{'connections': {'power_storage': []},
                                                                 'amount': 1}]

    # game_config['solar_pv_array_mars'] is a dict, not a label like the labelps assigned above.
    # So it needs it's own function
    pv_mars = 'solar_pv_array_mars'
    if pv_mars in game_config:
        amount = game_config[pv_mars].get('amount', 0)
        full_game_config['agents'][pv_mars] = [{'connections': {'power_storage': []},
                                                'amount': amount}]

    # If the front_end specifies an amount for this agent, overwrite any default values with the
    # specified value
    for x, y in full_game_config['agents'].items():
        if x in game_config and 'amount' in game_config[x] and game_config[x]['amount']:
            y[0]['amount'] = game_config[x]['amount']

    # Plants are treated separately because its a list of items which must be assigned as agents
    if 'plants' in game_config:
        for plant in game_config['plants']:
            agent_type = plant.get('species', None)
            amount = plant.get('amount', 0)
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


def calc_step_in_out(direction, currencies, step_record_data):
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
        currency = step.currency_type.name
        if step.direction == direction and currency in output:
            output[currency]['value'] += step.value
            output[currency]['unit'] = step.unit

    return output


def calc_step_storage_ratios(agents, model_record_data):
    """
    Calculate the ratio for the requested currencies for the requested <agent_type>_<agent_id>.

    Called from: route views.get_step()

    Input: agents = dictionary of agents for which to calculate ratios. For each agent, give a list
    of the currencies which should be included in the output. e.g. {'air_storage_1': ['atmo_co2']}.
    step_record_data = StepRecord for this step_num.

    Output: dictionary of agents, each agent has a dictionary of currency:ratio pairs. e.g.
    {'air_storage_1': {'atmo_co2': 0.21001018914835098}
    """

    capacity_data = StorageCapacityRecord.query.filter_by(model_record=model_record_data).all()

    output = {}
    for agent in agents:
        agent_type = agent[:agent.rfind('_')]
        agent_id = int(agent[agent.rfind('_')+1:])
        agent_capacities = [record for record in capacity_data
                            if record.agent_type.name == agent_type
                            and record.storage_id == agent_id]

        # First, get sum of all currencies
        total_value = 0
        unit = ''
        for record in agent_capacities:
            total_value += record.value
            if unit == '':
                unit = record.unit
            else:
                if not record.unit == unit:
                    sys.exit('ERROR in front_end_routes.calc_step_storage_ratios().'
                             'Currencies do not have same units.', unit, record.unit)

        output[agent] = {}
        # Now, calculate the ratio for specified currencies.
        for currency in agents[agent]:
            c_step_data = [record for record in agent_capacities
                           if record.currency_type.name == currency][0]
            output[agent][currency] = c_step_data.value / total_value

    return output


def parse_step_data(model_record_data, filters, step_record_data):
    reduced_output = model_record_data.get_data()
    if len(filters) == 0:
        return reduced_output
    for f in filters:
        if f == 'agent_type_counters':
            reduced_output[f] = [i.get_data() for i in model_record_data.agent_type_counters]
        if f == 'agent_type_counters':
            reduced_output[f] = [i.get_data() for i in model_record_data.storage_capacities]
        if f == 'agent_logs':
            reduced_output[f] = [i.get_data() for i in step_record_data.all()]
        else:
            print(f'WARNING: No parse_filters option {filter} in game_runner.parse_step_data.')
    return reduced_output


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

    agent_counters = AgentTypeCountRecord.query.filter_by(model_record=model_record_data).all()
    for record in agent_counters:
        if record.agent_type.name in output:
            output[record.agent_type.name] += record.agent_counter

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


def calc_step_storage_capacities(agent_types, model_record_data):
    output = {}
    storage_capacities = StorageCapacityRecord.query \
        .filter_by(model_record=model_record_data).all()
    for record in storage_capacities:
        agent_type = record.agent_type.name
        storage_id = record.storage_id
        currency = record.currency_type.name
        if (len(agent_types) == 0 or
           (agent_type in agent_types and
            (currency in agent_types[agent_type] or
             len(agent_types[agent_type]) == 0))):
            if agent_type not in output:
                output[agent_type] = {}
            if storage_id not in output[agent_type]:
                output[agent_type][storage_id] = {}
            output[agent_type][storage_id][currency] = {'value': record.value,
                                                        'unit': record.unit}
    return output


def get_growth_rates(agent_types, step_record_data):
    output = {}
    for agent_type in agent_types:
        output[agent_type] = None
    for step in step_record_data:
        agent_type = step.agent_type.name
        if agent_type in output and step.growth:
            if not output[agent_type] or step.growth > output[agent_type]:
                output[agent_type] = step.growth
    return output
