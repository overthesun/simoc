from . import util
from collections import OrderedDict
from simoc_server.database.db_model import AgentType, AgentTypeAttribute
import json


def seed(config_file):
    with open(config_file, 'r') as f:
        abm_config = json.load(f)
    plants = abm_config['agriculture']['plants']

    plant_data = {}
    for plant in plants:
        name = list(plant.keys())[0]
        agent_type = AgentType(name=name)
        plant_data["{0}_plant_agent_type".format(name)] = agent_type
        create_agent_type_attr(agent_type, 'char_class', 'plants')
        for attr in plant[name]['data']['characteristics']:
            attr_name = 'char_{}'.format(attr['type'])
            attr_value = attr['value'] if 'value' in attr else ''
            attr_units = attr['unit'] if 'unit' in attr else ''
            create_agent_type_attr(agent_type, attr_name, attr_value, attr_units)
        for attr in plant[name]['data']['input']:
            attr_name = 'in_{}'.format(attr['type'])
            attr_value = attr['value'] if 'value' in attr else ''
            attr_daytime_period = attr['daytime_period'] if 'daytime_period' in attr else ''
            attr_units = '{}/{}/{}'.format(attr['flow_rate']['unit'], attr['flow_rate']['time'], attr_daytime_period)
            create_agent_type_attr(agent_type, attr_name, attr_value, attr_units)
        for attr in plant[name]['data']['output']:
            attr_type = attr['type'] if 'type' in attr else ''
            attr_name = 'out_{}'.format(attr['type'])
            attr_value = attr['value'] if 'value' in attr else ''
            attr_daytime_period = attr['daytime_period'] if 'daytime_period' in attr else ''
            attr_units = '{}/{}/{}'.format(attr['flow_rate']['unit'], attr['flow_rate']['time'], attr_daytime_period)
            create_agent_type_attr(agent_type, attr_name, attr_value, attr_units)
    util.add_all(plant_data)

    for agent_class in ['inhabitants', 'storage', 'eclss', 'structures', 'power_generation']:
        agents = abm_config[agent_class]
        agent_data = {}
        for name in agents:
            agent_type = AgentType(name=name)
            agent_data["{}_{}_agent_type".format(name, agent_class)] = agent_type
            create_agent_type_attr(agent_type, 'char_class', agent_class)
            for attr in agents[name]['data']['characteristics']:
                attr_name = 'char_{}'.format(attr['type'])
                attr_value = attr['value'] if 'value' in attr else ''
                attr_units = attr['unit'] if 'unit' in attr else ''
                create_agent_type_attr(agent_type, attr_name, attr_value, attr_units)
            for attr in agents[name]['data']['input']:
                attr_name = 'in_{}'.format(attr['type'])
                attr_value = attr['value'] if 'value' in attr else ''
                attr_daytime_period = attr['daytime_period'] if 'daytime_period' in attr else ''
                attr_units = '{}/{}/{}'.format(attr['flow_rate']['unit'], attr['flow_rate']['time'],
                                               attr_daytime_period)
                create_agent_type_attr(agent_type, attr_name, attr_value, attr_units)
            for attr in agents[name]['data']['output']:
                attr_name = 'out_{}'.format(attr['type'])
                attr_value = attr['value'] if 'value' in attr else ''
                attr_daytime_period = attr['daytime_period'] if 'daytime_period' in attr else ''
                attr_units = '{}/{}/{}'.format(attr['flow_rate']['unit'], attr['flow_rate']['time'],
                                               attr_daytime_period)
                create_agent_type_attr(agent_type, attr_name, attr_value, attr_units)
        util.add_all(agent_data)


def create_agent_type_attr(agent_type, name, value, units=None, description=None):
    return AgentTypeAttribute(name=name, agent_type=agent_type, value=str(value),
        value_type=str(type(value).__name__), units=units, description=description)
