import json

from . import util
from simoc_server import db
from simoc_server.agent_model.agents import growth_func
from simoc_server.database.db_model import AgentType, AgentTypeAttribute
from simoc_server.util import location_to_day_length_minutes


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
            create_agent_type_attr(agent_type=agent_type, name=attr_name, value=attr_value,
                                   details=attr_units, description=None, growth=0)
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
                create_agent_type_attr(agent_type=agent_type, name=attr_name, value=attr_value,
                                       details=json.dumps(attr_details), description=None,
                                       growth=1 if growth else 0)
    util.add_all(agent_data)
    calculate_growth_coef()


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


def create_agent_type_attr(agent_type, name, value, details=None, description=None, growth=None):
    """TODO

    TODO

    Args:
      agent_type: TODO
      name: TODO
      value: TODO
      growth: TODO
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
                              description=description,
                              growth=growth)


def calculate_growth_coef():
    agents = AgentType.query.all()
    for agent in agents:
        location = AgentTypeAttribute.query.filter_by(agent_type=agent,
                                                      name='char_location').first()
        if location is None:
            location = 'mars'
        else:
            location = location.value
        lifetime = AgentTypeAttribute.query.filter_by(agent_type=agent,
                                                      name='char_lifetime').first()
        if lifetime is not None:
            lifetime = float(lifetime.value)
        else:
            lifetime = 1
        agent_type_attrs = AgentTypeAttribute.query.filter_by(agent_type=agent, growth=1).all()
        for attr in agent_type_attrs:
            update = False
            details = json.loads(attr.details)
            if details['lifetime_growth_type'] in ['norm', 'normal'] \
                    and details['lifetime_growth_scale'] == '':
                mean_value = float(attr.value)
                day_length_minutes = location_to_day_length_minutes(location)
                day_length_hours = day_length_minutes / 60
                num_values = int(lifetime * day_length_hours + 1)
                center = details['lifetime_growth_center']
                center = float(center) if len(center) > 0 else None
                min_value = details['lifetime_growth_min_value']
                min_value = float(min_value) if len(min_value) > 0 else 0
                invert = details['lifetime_growth_invert']
                invert = bool(invert) if len(invert) > 0 else False
                res = growth_func.optimize_bell_curve_mean(mean_value=mean_value,
                                                           num_values=num_values,
                                                           center=center,
                                                           min_value=min_value,
                                                           invert=invert,
                                                           noise=False)
                details['lifetime_growth_scale'] = str(res['scale'])
                attr.value = str(res['max_value'])
                update = True
            elif details['lifetime_growth_type'] in ['sig', 'sigmoid'] \
                    and details['lifetime_growth_steepness'] == '':
                mean_value = float(attr.value)
                day_length_minutes = location_to_day_length_minutes(location)
                day_length_hours = day_length_minutes / 60
                num_values = int(lifetime * day_length_hours + 1)
                center = details['lifetime_growth_center']
                center = float(center) if len(center) > 0 else None
                min_value = details['lifetime_growth_min_value']
                min_value = float(min_value) if len(min_value) > 0 else 0
                res = growth_func.optimize_sigmoid_curve_mean(mean_value=mean_value,
                                                              num_values=num_values,
                                                              center=center,
                                                              min_value=min_value,
                                                              noise=False)
                details['lifetime_growth_steepness'] = str(res['steepness'])
                attr.value = str(res['max_value'])
                update = True
            if details['daily_growth_type'] in ['norm', 'normal'] \
                    and details['daily_growth_scale'] == '':
                mean_value = float(attr.value)
                day_length_minutes = location_to_day_length_minutes(location)
                day_length_hours = day_length_minutes / 60
                day_length = int(day_length_hours)
                center = details['daily_growth_center']
                center = float(center) if len(center) > 0 else None
                min_rate = details['daily_growth_min_rate']
                min_value = float(min_rate) * mean_value if len(min_rate) else 0
                invert = details['daily_growth_invert']
                invert = bool(invert) if len(invert) > 0 else False
                res = growth_func.optimize_bell_curve_mean(mean_value=mean_value,
                                                           num_values=day_length,
                                                           center=center,
                                                           min_value=min_value,
                                                           invert=invert,
                                                           noise=False)
                details['daily_growth_scale'] = str(res['scale'])
                update = True
            elif details['daily_growth_type'] in ['sig', 'sigmoid'] \
                    and details['daily_growth_steepness'] == '':
                mean_value = float(attr.value)
                day_length_minutes = location_to_day_length_minutes(location)
                day_length_hours = day_length_minutes / 60
                day_length = int(day_length_hours)
                center = details['daily_growth_center']
                center = float(center) if center else None
                min_rate = details['daily_growth_min_rate']
                min_value = float(min_rate) * mean_value if min_rate else 0
                res = growth_func.optimize_sigmoid_curve_mean(mean_value=mean_value,
                                                              num_values=day_length,
                                                              center=center,
                                                              min_value=min_value,
                                                              noise=False)
                details['daily_growth_steepness'] = str(res['steepness'])
                update = True
            if update:
                db.session.delete(attr)
                new_attr = AgentTypeAttribute(name=attr.name, agent_type=agent,
                                              value=attr.value,
                                              value_type=str(type(attr.value).__name__),
                                              details=json.dumps(details),
                                              description=attr.description,
                                              growth=attr.growth)
                db.session.add(new_attr)
                db.session.commit()
