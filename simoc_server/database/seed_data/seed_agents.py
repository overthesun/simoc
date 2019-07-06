import json
import random

from . import util
from simoc_server import db
from simoc_server.agent_model.agents import growth_func
from simoc_server.database.db_model import AgentType, AgentTypeAttribute, \
    AgentTypeAttributeDetails, CurrencyType
from simoc_server.util import location_to_day_length_minutes

_GLOBAL_CURRENCY_LIST = {}


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
            currency = None
            if attr['type'].startswith('capacity'):
                currency = attr['type'].split('_', 1)[1]
                if currency not in _GLOBAL_CURRENCY_LIST:
                    _GLOBAL_CURRENCY_LIST[currency] = CurrencyType(name=currency,
                                                                   id=random.randint(1, 1e7))
            currency_type = _GLOBAL_CURRENCY_LIST[currency] if currency else None
            agent_type_attribute = AgentTypeAttribute(name=attr_name,
                                                      agent_type=agent_type,
                                                      value=str(attr_value),
                                                      value_type=str(type(attr_value).__name__),
                                                      description=None)
            AgentTypeAttributeDetails(agent_type_attribute=agent_type_attribute,
                                      agent_type=agent_type,
                                      currency_type=currency_type,
                                      units=attr_units)
        for section in ['input', 'output']:
            for attr in agents[name]['data'][section]:
                prefix = 'in' if section == 'input' else 'out'
                currency = attr['type'].lower().strip()
                attr_name = '{}_{}'.format(prefix, currency)
                attr_value = attr.get("value", None)
                is_required = attr.get("required", None)
                requires = attr.get("requires", None)
                deprive_unit = None
                deprive_value = None
                flow_unit = None
                flow_time = None
                criteria_name = None
                criteria_limit = None
                criteria_value = None
                criteria_buffer = None
                lifetime_growth_type = None
                lifetime_growth_center = None
                lifetime_growth_min_value = None
                lifetime_growth_max_value = None
                lifetime_growth_min_threshold = None
                lifetime_growth_max_threshold = None
                lifetime_growth_invert = None
                lifetime_growth_noise = None
                lifetime_growth_steepness = None
                lifetime_growth_scale = None
                daily_growth_type = None
                daily_growth_center = None
                daily_growth_min_value = None
                daily_growth_max_value = None
                daily_growth_min_threshold = None
                daily_growth_max_threshold = None
                daily_growth_invert = None
                daily_growth_noise = None
                daily_growth_scale = None
                daily_growth_steepness = None
                deprive = attr.get("deprive", None)
                if deprive:
                    deprive_unit = deprive.get('unit', None)
                    deprive_value = deprive.get('value', None)
                flow_rate = attr.get("flow_rate", None)
                if flow_rate:
                    flow_unit = flow_rate.get('unit', None)
                    flow_time = flow_rate.get('time', None)
                criteria = attr.get("criteria", None)
                if criteria:
                    criteria_name = criteria.get('name', None)
                    criteria_limit = criteria.get('limit', None)
                    criteria_value = criteria.get('value', None)
                    criteria_buffer = criteria.get('buffer', None)
                is_growing = 0
                growth = attr.get("growth", None)
                if growth:
                    is_growing = 1
                    lifetime_growth = growth.get('lifetime', None)
                    if lifetime_growth:
                        lifetime_growth_type = lifetime_growth.get('type', None)
                        lifetime_growth_center = lifetime_growth.get('center', None)
                        lifetime_growth_min_value = lifetime_growth.get('min_value', None)
                        lifetime_growth_max_value = lifetime_growth.get('man_value', None)
                        lifetime_growth_min_threshold = lifetime_growth.get('min_threshold', None)
                        lifetime_growth_max_threshold = lifetime_growth.get('max_threshold', None)
                        lifetime_growth_invert = lifetime_growth.get('invert', None)
                        lifetime_growth_noise = lifetime_growth.get('noise', None)
                        lifetime_growth_scale = lifetime_growth.get('scale', None)
                        lifetime_growth_steepness = lifetime_growth.get('steepness', None)
                    daily_growth = growth.get('daily', None)
                    if daily_growth:
                        daily_growth_type = daily_growth.get('type', None)
                        daily_growth_center = daily_growth.get('center', None)
                        daily_growth_min_value = daily_growth.get('min_value', None)
                        daily_growth_max_value = daily_growth.get('man_value', None)
                        daily_growth_min_threshold = daily_growth.get('min_threshold', None)
                        daily_growth_max_threshold = daily_growth.get('max_threshold', None)
                        daily_growth_invert = daily_growth.get('invert', None)
                        daily_growth_noise = daily_growth.get('noise', None)
                        daily_growth_scale = daily_growth.get('scale', None)
                        daily_growth_steepness = daily_growth.get('steepness', None)
                agent_type_attribute = AgentTypeAttribute(name=attr_name,
                                                          agent_type=agent_type,
                                                          value=str(attr_value),
                                                          value_type=str(type(attr_value).__name__),
                                                          description=None)
                if currency not in _GLOBAL_CURRENCY_LIST:
                    _GLOBAL_CURRENCY_LIST[currency] = CurrencyType(name=currency,
                                                                   id=random.randint(1, 1e7))
                attr_details = {'agent_type_attribute':  agent_type_attribute,
                                'agent_type': agent_type,
                                'currency_type': _GLOBAL_CURRENCY_LIST[currency],
                                'flow_unit': flow_unit,
                                'flow_time': flow_time,
                                'criteria_name': criteria_name,
                                'criteria_limit': criteria_limit,
                                'criteria_value': criteria_value,
                                'criteria_buffer': criteria_buffer,
                                'deprive_unit': deprive_unit,
                                'deprive_value': deprive_value,
                                'is_required': is_required,
                                'requires': requires,
                                'is_growing': is_growing,
                                'lifetime_growth_type': lifetime_growth_type,
                                'lifetime_growth_center': lifetime_growth_center,
                                'lifetime_growth_min_value': lifetime_growth_min_value,
                                'lifetime_growth_max_value': lifetime_growth_max_value,
                                'daily_growth_type': daily_growth_type,
                                'daily_growth_center': daily_growth_center,
                                'daily_growth_min_value': daily_growth_min_value,
                                'daily_growth_max_value': daily_growth_max_value,
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
                AgentTypeAttributeDetails(**attr_details)
    util.add_all(agent_data)
    # calculate_growth_coef()


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
        agent_type_attribute_details = AgentTypeAttributeDetails.query.filter_by(agent_type=agent,
                                                                                 is_growing=1).all()
        for attr_details in agent_type_attribute_details:
            attr = AgentTypeAttribute.query.filter_by(id=attr_details['agent_type_attribute_id']).first()
            update = False
            if attr_details['lifetime_growth_type'] in ['norm', 'normal'] \
                    and attr_details['lifetime_growth_scale'] is None:
                mean_value = float(attr.value)
                day_length_minutes = location_to_day_length_minutes(location)
                day_length_hours = day_length_minutes / 60
                num_values = int(lifetime * day_length_hours + 1)
                center = attr_details['lifetime_growth_center'] or num_values // 2
                min_value = attr_details['lifetime_growth_min_value'] or 0
                invert = attr_details['lifetime_growth_invert']
                res = growth_func.optimize_bell_curve_mean(mean_value=mean_value,
                                                           num_values=num_values,
                                                           center=center,
                                                           min_value=min_value,
                                                           invert=invert,
                                                           noise=False)
                attr_details['lifetime_growth_scale'] = float(res['scale'])
                attr.value = float(res['max_value'])
                update = True
            elif attr_details['lifetime_growth_type'] in ['sig', 'sigmoid'] \
                    and attr_details['lifetime_growth_steepness'] is None:
                mean_value = float(attr.value)
                day_length_minutes = location_to_day_length_minutes(location)
                day_length_hours = day_length_minutes / 60
                num_values = int(lifetime * day_length_hours + 1)
                center = attr_details['lifetime_growth_center'] or num_values // 2
                min_value = attr_details['lifetime_growth_min_value'] or 0
                res = growth_func.optimize_sigmoid_curve_mean(mean_value=mean_value,
                                                              num_values=num_values,
                                                              center=center,
                                                              min_value=min_value,
                                                              noise=False)
                attr_details['lifetime_growth_steepness'] = float(res['steepness'])
                attr.value = float(res['max_value'])
                update = True
            if attr_details['daily_growth_type'] in ['norm', 'normal'] \
                    and attr_details['daily_growth_scale'] is None:
                mean_value = float(attr.value)
                day_length_minutes = location_to_day_length_minutes(location)
                day_length_hours = day_length_minutes / 60
                day_length = int(day_length_hours)
                center = attr_details['daily_growth_center'] or day_length // 2
                min_value = attr_details['daily_growth_min_value'] or 0
                invert = attr_details['daily_growth_invert']
                res = growth_func.optimize_bell_curve_mean(mean_value=mean_value,
                                                           num_values=day_length,
                                                           center=center,
                                                           min_value=min_value,
                                                           invert=invert,
                                                           noise=False)
                attr_details['daily_growth_scale'] = float(res['scale'])
                update = True
            elif attr_details['daily_growth_type'] in ['sig', 'sigmoid'] \
                    and attr_details['daily_growth_steepness'] is None:
                mean_value = float(attr.value)
                day_length_minutes = location_to_day_length_minutes(location)
                day_length_hours = day_length_minutes / 60
                day_length = int(day_length_hours)
                center = attr_details['daily_growth_center'] or day_length // 2
                min_value = attr_details['daily_growth_min_rate'] or 0
                res = growth_func.optimize_sigmoid_curve_mean(mean_value=mean_value,
                                                              num_values=day_length,
                                                              center=center,
                                                              min_value=min_value,
                                                              noise=False)
                attr_details['daily_growth_steepness'] = float(res['steepness'])
                update = True
            if update:
                db.session.delete(attr)
                db.session.delete(attr_details)
                new_attr = AgentTypeAttribute(id=attr.id,
                                              name=attr.name,
                                              agent_type=agent,
                                              value=attr.value,
                                              value_type=str(type(attr.value).__name__),
                                              description=None)
                new_attr_details = AgentTypeAttributeDetails(**attr_details.get_data())
                db.session.add_all([new_attr, new_attr_details])
                db.session.commit()
