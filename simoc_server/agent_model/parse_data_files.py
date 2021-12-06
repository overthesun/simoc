import json
import random

from simoc_server.agent_model.agents import growth_func
from simoc_server.util import location_to_day_length_minutes
from simoc_server.exceptions import AgentModelInitializationError

def parse_currency_desc(currency_desc):
    parsed = {}
    for currency_class, currencies in currency_desc.items():
        currency_class_record = {'name': currency_class,
                                 'id': random.getrandbits(32),
                                 'type': 'currency_class',
                                 'currencies': list(currencies.keys())}
        parsed[currency_class] = currency_class_record
        for currency, currency_data in currencies.items():
            currency_record = {'name': currency,
                                'id': random.getrandbits(32),
                                'type': 'currency',
                                'class': currency_class,
                                **currency_data}
            parsed[currency] = currency_record
    return parsed

def parse_agent_desc(config, currencies, agent_desc):
    """TODO

    TODO

    Args:
      currencies: A dict of parsed data from currency_desc.json
      agent_desc: Raw data from agent_desc.json
    """
    agent_data = {}
    currencies_list = currencies.keys()
    location = config.get('location', 'mars')
    agent_class_reference = {}
    for agent_class, agents in agent_desc.items():
        for agent in agents.keys():
            agent_class_reference[agent] = agent_class
    for agent in config['agents'].keys():
        agent_class = agent_class_reference.get(agent, None)
        if not agent_class:
            raise AgentModelInitializationError(f"No agent_desc data found for {agent}")
        parsed_agent_data = parse_agent(agent_class,
                                        agent,
                                        agent_desc[agent_class][agent],
                                        currencies_list,
                                        location)
        agent_data[agent] = parsed_agent_data
    return agent_data

def parse_agent(agent_class, name, data, currencies, location):
    """TODO

    TODO

    Args:
      agent_class: TODO
      agent: TODO
    """
    # Initialize return object
    agent_data = {
        "agent_class": agent_class,
        "agent_type_id": random.getrandbits(32),
        "attributes": {},
        "attribute_details": {},
    }

    # Parse characteristics
    for attr in data['data']['characteristics']:
        # Attributes
        attr_name = 'char_{}'.format(attr['type'])
        attr_value = attr.get("value", '')
        agent_data['attributes'][attr_name] = attr_value
        # Attribute Details
        attr_units = attr.get("unit", '')
        currency = None
        if attr['type'].startswith('capacity'):
            currency = attr['type'].split('_', 1)[1]
            if currency not in currencies:
                raise AgentModelInitializationError(f"Currency data not found for {currency} when parsing {name}.")
        attribute_detail = dict(currency_type=currency,
                                units=attr_units)
        agent_data['attribute_details'][attr_name] = attribute_detail

    # Parse currency exchanges (inputs & outputs)
    for section in ['input', 'output']:
        for attr in data['data'][section]:
            currency = attr['type'].lower().strip()
            if currency not in currencies:
                raise AgentModelInitializationError(f"Currency data not found for {currency} when parsing {name}.")

            # Attributes
            prefix = 'in' if section == 'input' else 'out'
            attr_name = '{}_{}'.format(prefix, currency)
            attr_value = attr.get("value", None)
            agent_data['attributes'][attr_name] = attr_value

            # Attribute details
            deprive = attr.get("deprive", None)
            flow_rate = attr.get("flow_rate", None)
            criteria = attr.get("criteria", None)
            growth = attr.get("growth", None)
            lifetime_growth = None if not growth else growth.get('lifetime', None)
            daily_growth = None if not growth else growth.get('daily', None)
            attribute_detail = dict(
                currency_type=currency,
                flow_unit=None if not flow_rate else flow_rate.get('unit', None),
                flow_time=None if not flow_rate else flow_rate.get('time', None),
                weighted=attr.get("weighted", None),
                criteria_name=None if not criteria else criteria.get('name', None),
                criteria_limit=None if not criteria else criteria.get('limit', None),
                criteria_value=None if not criteria else criteria.get('value', None),
                criteria_buffer=None if not criteria else criteria.get('buffer', None),
                deprive_unit=None if not deprive else deprive.get('unit', None),
                deprive_value=None if not deprive else deprive.get('value', None),
                is_required=attr.get("required", None),
                requires=attr.get("requires", None),
                is_growing=0 if not growth else 1,
                lifetime_growth_type=None if not lifetime_growth else lifetime_growth.get('type', None),
                lifetime_growth_center=None if not lifetime_growth else lifetime_growth.get('center', None),
                lifetime_growth_min_value=None if not lifetime_growth else lifetime_growth.get('min_value', None),
                lifetime_growth_max_value=None if not lifetime_growth else lifetime_growth.get('max_value', None),
                lifetime_growth_min_threshold=None if not lifetime_growth else lifetime_growth.get('min_threshold', None),
                lifetime_growth_max_threshold=None if not lifetime_growth else lifetime_growth.get('max_threshold', None),
                lifetime_growth_invert=None if not lifetime_growth else lifetime_growth.get('invert', None),
                lifetime_growth_noise=None if not lifetime_growth else lifetime_growth.get('noise', None),
                lifetime_growth_scale=None if not lifetime_growth else lifetime_growth.get('scale', None),
                lifetime_growth_steepness=None if not lifetime_growth else lifetime_growth.get('steepness', None),
                daily_growth_type=None if not daily_growth else daily_growth.get('type', None),
                daily_growth_center=None if not daily_growth else daily_growth.get('center', None),
                daily_growth_min_value=None if not daily_growth else daily_growth.get('min_value', None),
                daily_growth_max_value=None if not daily_growth else daily_growth.get('max_value', None),
                daily_growth_min_threshold=None if not daily_growth else daily_growth.get('min_threshold', None),
                daily_growth_max_threshold=None if not daily_growth else daily_growth.get('max_threshold', None),
                daily_growth_invert=None if not daily_growth else daily_growth.get('invert', None),
                daily_growth_noise=None if not daily_growth else daily_growth.get('noise', None),
                daily_growth_scale=None if not daily_growth else daily_growth.get('scale', None),
                daily_growth_steepness=None if not daily_growth else daily_growth.get('steepness', None))

            if attribute_detail['lifetime_growth_type'] in ['norm', 'normal'] \
                    and attribute_detail['lifetime_growth_scale'] is None:
                lifetime = agent_data['attributes'].get('char_lifetime', 1)
                lgmv = calculate_lifetime_growth_max_value(attr_value,
                                                           attribute_detail,
                                                           lifetime,
                                                           location)
                attribute_detail['lifetime_growth_max_value'] = lgmv

            agent_data['attribute_details'][attr_name] = attribute_detail

    return agent_data

def calculate_lifetime_growth_max_value(attr_value, attr_details, lifetime, location):
    mean_value = float(attr_value)
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
    # Rounding is not technically necessary, but it was rounded under the old
    # system and I do it here for continuity of test results.
    return round(float(res['max_value']), 8)
