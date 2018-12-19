from . import util
from simoc_server.database.db_model import AgentType, AgentTypeAttribute
import json


def import_agents(agents, agent_class):
    agent_data = {}
    for name in agents:
        if not agents[name].get('data', None):
            continue
        agent_type = AgentType(name=name, agent_class=agent_class)
        agent_data["{}_{}_agent_type".format(name, agent_class)] = agent_type
        for attr in agents[name]['data']['characteristics']:
            attr_name = 'char_{}'.format(attr['type'])
            attr_value = attr.get("value", '')
            attr_units = attr.get("unit", '')
            create_agent_type_attr(agent_type, attr_name, attr_value, attr_units)
        for section in ['input', 'output']:
            for attr in agents[name]['data'][section]:
                prefix = 'in' if section == 'input' else 'out'
                attr_name = '{}_{}'.format(prefix, attr['type'])
                attr_value = attr.get("value", '')
                attr_active_period = attr.get("active_period", '')
                deprive = attr.get("deprive", None)
                flow_rate = attr.get("flow_rate", None)
                growth = attr.get("growth", None)
                criteria = attr.get("criteria", None)
                required = attr.get("required", None)
                requires = attr.get("requires", None)
                if requires is not None:
                    requires = "#".join(requires)
                deprive_unit, deprive_value = '', ''
                flow_unit, flow_time = '', ''
                cr_name, cr_limit, cr_value, cr_buffer = '', '', '', ''
                if deprive:
                    deprive_unit = deprive.get('unit', '')
                    deprive_value = deprive.get('value', '')
                if flow_rate:
                    flow_unit = flow_rate.get('unit', '')
                    flow_time = flow_rate.get('time', '')
                if criteria:
                    cr_name = criteria.get('name', '')
                    cr_limit = criteria.get('limit', '')
                    cr_value = criteria.get('value', '')
                    cr_buffer = criteria.get('buffer', '')
                attr_descriptions = '{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}'.format(flow_unit, flow_time, attr_active_period, cr_name, cr_limit, cr_value, cr_buffer, deprive_unit, deprive_value, required, requires, growth)
                create_agent_type_attr(agent_type, attr_name, attr_value, attr_descriptions)
    util.add_all(agent_data)



def seed(config_file):
    with open(config_file, 'r') as f:
        abm_config = json.load(f)
    for agent_class in abm_config:
        import_agents(abm_config[agent_class], agent_class)


def create_agent_type_attr(agent_type, name, value, units=None, description=None):
    return AgentTypeAttribute(name=name, agent_type=agent_type, value=str(value),
        value_type=str(type(value).__name__), units=units, description=description)
