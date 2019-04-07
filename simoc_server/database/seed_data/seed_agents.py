import json

from simoc_server.database.db_model import AgentType, AgentTypeAttribute
from . import util


def import_agents(agents, agent_class):
    """TODO

    TODO

    Args:
      agents: TODO
      agent_class: TODO
    """
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
                is_required = str(attr.get("required", ''))
                requires = attr.get("requires", '')
                if requires is not None:
                    requires = "#".join(requires)
                deprive = attr.get("deprive", None)
                deprive_unit = ''
                deprive_value = ''
                if deprive:
                    deprive_unit = deprive.get('unit', '')
                    deprive_value = str(deprive.get('value', ''))
                flow_rate = attr.get("flow_rate", None)
                flow_unit = ''
                flow_time = ''
                if flow_rate:
                    flow_unit = flow_rate.get('unit', '')
                    flow_time = flow_rate.get('time', '')
                criteria = attr.get("criteria", None)
                cr_name = ''
                cr_limit = ''
                cr_value = ''
                cr_buffer = ''
                if criteria:
                    cr_name = criteria.get('name', '')
                    cr_limit = criteria.get('limit', '')
                    cr_value = str(criteria.get('value', ''))
                    cr_buffer = str(criteria.get('buffer', ''))
                lifetime_growth_type = ''
                lifetime_growth_center = ''
                lifetime_growth_min_value = ''
                lifetime_growth_min_threshold = ''
                lifetime_growth_max_threshold = ''
                lifetime_growth_invert = ''
                lifetime_growth_noise = ''
                lifetime_growth_steepness = ''
                lifetime_growth_scale = ''
                daily_growth_type = ''
                daily_growth_center = ''
                daily_growth_min_rate = ''
                daily_growth_min_threshold = ''
                daily_growth_max_threshold = ''
                daily_growth_invert = ''
                daily_growth_noise = ''
                daily_growth_scale = ''
                daily_growth_steepness = ''
                growth = attr.get("growth", None)
                if growth:
                    lifetime_growth = growth.get('lifetime', None)
                    if lifetime_growth:
                        lifetime_growth_type = lifetime_growth.get('type', '')
                        lifetime_growth_center = str(lifetime_growth.get('center', ''))
                        lifetime_growth_min_value = str(lifetime_growth.get('min_value', ''))
                        lifetime_growth_min_threshold = str(lifetime_growth.get('min_threshold', ''))
                        lifetime_growth_max_threshold = str(lifetime_growth.get('max_threshold', ''))
                        lifetime_growth_invert = str(lifetime_growth.get('invert', ''))
                        lifetime_growth_noise = str(lifetime_growth.get('noise', ''))
                        lifetime_growth_scale = str(lifetime_growth.get('scale', ''))
                        lifetime_growth_steepness = str(lifetime_growth.get('steepness', ''))
                    daily_growth = growth.get('daily', None)
                    if daily_growth:
                        daily_growth_type = daily_growth.get('type', '')
                        daily_growth_center = str(daily_growth.get('center', ''))
                        daily_growth_min_rate = str(daily_growth.get('min_rate', ''))
                        daily_growth_min_threshold = str(daily_growth.get('min_threshold', ''))
                        daily_growth_max_threshold = str(daily_growth.get('max_threshold', ''))
                        daily_growth_invert = str(daily_growth.get('invert', ''))
                        daily_growth_noise = str(daily_growth.get('noise', ''))
                        daily_growth_scale = str(daily_growth.get('scale', ''))
                        daily_growth_steepness = str(daily_growth.get('steepness', ''))
                attr_details = {'flow_unit': flow_unit,
                                'flow_time': flow_time,
                                'cr_name': cr_name,
                                'cr_limit': cr_limit,
                                'cr_value': cr_value,
                                'cr_buffer': cr_buffer,
                                'deprive_unit': deprive_unit,
                                'deprive_value': deprive_value,
                                'is_required': is_required,
                                'requires': requires,
                                'lifetime_growth_type': lifetime_growth_type,
                                'lifetime_growth_center': lifetime_growth_center,
                                'lifetime_growth_min_value': lifetime_growth_min_value,
                                'daily_growth_type': daily_growth_type,
                                'daily_growth_center': daily_growth_center,
                                'daily_growth_min_rate': daily_growth_min_rate,
                                'lifetime_growth_min_threshold': lifetime_growth_min_threshold,
                                'lifetime_growth_max_threshold': lifetime_growth_max_threshold,
                                'daily_growth_min_threshold': daily_growth_min_threshold,
                                'daily_growth_max_threshold': daily_growth_max_threshold,
                                'daily_growth_invert': daily_growth_invert,
                                'lifetime_growth_invert': lifetime_growth_invert,
                                'daily_growth_noise': daily_growth_noise,
                                'lifetime_growth_noise': lifetime_growth_noise,
                                'daily_growth_scale': daily_growth_scale,
                                'lifetime_growth_scale': lifetime_growth_scale,
                                'daily_growth_steepness': daily_growth_steepness,
                                'lifetime_growth_steepness': lifetime_growth_steepness}
                create_agent_type_attr(agent_type, attr_name, attr_value, json.dumps(attr_details))
    util.add_all(agent_data)


def seed(config_file):
    """TODO

    TODO

    Args:
      config_file: TODO
    """
    with open(config_file, 'r') as f:
        abm_config = json.load(f)
    for agent_class in abm_config:
        import_agents(abm_config[agent_class], agent_class)


def create_agent_type_attr(agent_type, name, value, details=None, description=None):
    """TODO

    TODO

    Args:
      agent_type: TODO
      name: TODO
      value: TODO
      details: TODO
      description: TODO

    Returns:
      TODO
    """
    return AgentTypeAttribute(name=name,
                              agent_type=agent_type,
                              value=str(value),
                              value_type=str(type(value).__name__),
                              details=details,
                              description=description)
