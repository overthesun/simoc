import json
import random
from itertools import zip_longest

from agent_model.agents import growth_func
from agent_model.util import location_to_day_length_minutes

def parse_currency_desc(currency_desc):
    """Converts raw currency_desc into a dictionary of currencies and classes.

    Currencies input via currency_desc.json are stored organized heirarchically
    with individual currencies nested below currency classes. This function
    returns a dict of all currencies and classes on the same level with added
    'id', 'type' descriptor, 'class' descriptor for currencies and 'currencies'
    list for classes.

    Args:
      currency_desc: dict, raw data from currency_desc.json

    Returns:
      dict: All currencies and currency_classes with added IDs and metadata.
    """
    parsed = {}
    currency_errors = {}
    def _add(key, value):
        if key in parsed:
            currency_errors[key] = "All currencies and currency class names must be unique"
        else:
            parsed[key] = value
    for currency_class, currencies in currency_desc.items():
        currency_class_record = {'name': currency_class,
                                 'id': random.getrandbits(32),
                                 'type': 'currency_class',
                                 'currencies': list(currencies.keys())}
        _add(currency_class, currency_class_record)
        for currency, currency_data in currencies.items():
            currency_record = {'name': currency,
                                'id': random.getrandbits(32),
                                'type': 'currency',
                                'class': currency_class,
                                **currency_data}
            _add(currency, currency_record)
    return parsed, currency_errors

def parse_agent_desc(config, currencies, agent_desc, _DEFAULT_LOCATION):
    """Converts raw agent_desc.json data into AgentModel initialization dict

    Return an object that includes all required data for all agents included
    in `config`. Prior to 2022, this data was loaded into a database and
    referenced during runtime.

    Args:
      config: dict, raw game_config
      currencies: dict, output of parse_currecy_desc
      agent_desc: dict, raw data from agent_desc.json

    Returns:
      dict: Data for all agents needed to initialize AgentModel

    Raises:
      AgentModelInitializationError: If agent_desc or currency data is missing

    """
    agents_data = {}
    agents_errors = {}
    currencies_list = currencies.keys()
    location = config.get('location', _DEFAULT_LOCATION)
    agent_class_reference = {}
    for agent_class, agents in agent_desc.items():
        for agent in agents.keys():
            agent_class_reference[agent] = agent_class
    for agent in config['agents'].keys():
        agent_class = agent_class_reference.get(agent, None)
        if not agent_class or agent not in agent_desc[agent_class]:
            agents_errors[agent]['agent_class'] = "Agent not specified in agent_desc"
            continue
        parsed_agent_data, agent_errors = parse_agent(agent_class,
                                                      agent,
                                                      agent_desc[agent_class][agent],
                                                      currencies_list,
                                                      location)
        agents_data[agent] = parsed_agent_data
        if len(agent_errors) > 0:
            agents_errors[agent] = agent_errors
    return agents_data, agents_errors

def parse_agent(agent_class, name, data, currencies, location):
    """Converts agent_desc data for one agent into GeneralAgent initialization data

    Takes a sparse definition of agent parameters and returns dicts with all
    possible values, set to 'None' if not specified.
    """
    # Initialize return object
    agent_data = {
        "agent_class": agent_class,
        "agent_type_id": random.getrandbits(32),
        "attributes": {},
        "attribute_details": {},
    }
    agent_errors = {}

    # Parse characteristics
    for attr in data['data']['characteristics']:
        # Attributes
        attr_name = 'char_{}'.format(attr['type'])
        attr_value = attr.get("value", '')
        agent_data['attributes'][attr_name] = attr_value
        # Attribute Details
        attr_unit = attr.get("unit", '')
        currency = None
        if attr['type'].startswith('capacity'):
            currency = attr['type'].split('_', 1)[1]
            if currency not in currencies:
                agent_errors[currency] = "Currency not specified in currency_desc"
        attribute_detail = dict(currency_type=currency,
                                unit=attr_unit)
        agent_data['attribute_details'][attr_name] = attribute_detail

    # Parse currency exchanges (inputs & outputs)
    for section in ['input', 'output']:
        for attr in data['data'][section]:
            currency = attr['type'].lower().strip()
            if currency not in currencies:
                agent_errors[currency] = "Currency not specified in currency_desc"

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

    return agent_data, agent_errors

def parse_agent_conn(active_agents, agent_conn):
    """Returns active_connections dict from active_agent list and raw agent_conn.json"""
    conn_errors = {}

    # 1. SUBSTITUTE STRUCTURES
    # Some connections specify a structure class (e.g. 'habitat') rather than
    # a specific agent (e.g. 'crew_habitat_small') to accomodate different
    # configurations.
    def get_sub(agent_class):
        try:
            agent = next(a for a in active_agents if agent_class in a)
            return agent
        except StopIteration as e:
            return None
    structures_dict = {k: get_sub(k) for k in ['habitat', 'greenhouse']}
    def _substitute_structures(agent_type):
        if agent_type in structures_dict:
            return structures_dict[agent_type]
        return agent_type

    # 2. PARSE RELEVANT CONNECTIONS INTO DICT
    # Connections are specified in a long list and don't specify outbound or
    # inbound. Here we parse the list into a dict, indexed by agent names, for
    # both the from- and to- agent.
    connections_dict = {}
    for conn in agent_conn:
        from_agent, from_currency = conn['from'].split(".")
        to_agent, to_currency = conn['to'].split(".")
        priority = int(conn.get('priority', 0))
        from_agent = _substitute_structures(from_agent)
        to_agent = _substitute_structures(to_agent)
        if from_agent not in active_agents or to_agent not in active_agents:
            continue
        # Add agents to dict
        for agent in [from_agent, to_agent]:
            if agent not in connections_dict.keys():
                connections_dict[agent] = {'in': {}, 'out': {}}
        # Add currencies/connections by agent
        to_record = dict(agent_type=to_agent, priority=priority)
        if from_currency not in connections_dict[from_agent]['out']:
            connections_dict[from_agent]['out'][from_currency] = [to_record]
        else:
            connections_dict[from_agent]['out'][from_currency].append(to_record)
        from_record = dict(agent_type=from_agent, priority=priority)
        if to_currency not in connections_dict[to_agent]['in']:
            connections_dict[to_agent]['in'][to_currency] = [from_record]
        else:
            connections_dict[to_agent]['in'][to_currency].append(from_record)

    # 3. COMPILE CONNECTIONS FOR ACTIVE AGENTS
    active_connections = {}
    for agent in active_agents:
        if agent not in connections_dict:
            continue
        connections = connections_dict[agent]
        for prefix in ['in', 'out']:
            for currency, conns in connections[prefix].items():
                _sorted = sorted(conns, key=lambda c: c['priority'])
                connections[prefix][currency] = [c['agent_type'] for c in _sorted]
        active_connections[agent] = connections

    return active_connections, conn_errors

def calculate_lifetime_growth_max_value(attr_value, attr_details, lifetime, location):
    """Calculate the highest point on a normal bell curve"""
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

def parse_agent_events(agent_events):
    agents_data = {}
    agents_errors = {}
    for agent, events in agent_events.items():
        attrs = {}
        attr_details = {}
        agent_errors = {}
        def _error(index, message):
            if index not in agent_errors:
                agent_errors[index] = []
            agent_errors[index].append(message)
        for i, event in enumerate(events):
            for field in ['type', 'function', 'scope', 'probability']:
                if field not in event:
                    _error(str(i), f"Events must specify {field}")
            for field in ['probability', 'magnitude', 'duration']:
                if field in event and 'value' not in event[field]:
                    _error(str(i), f"Events with {field} must include a value")
            for field in ['magnitude', 'duration']:
                if 'variation' in event[field]:
                    variation = event[field]['variation']
                    if 'upper' not in variation or 'lower' not in variation:
                        _error(str(i), f"Events with {field} variation must specify upper or lower threshold")
                    if 'distribution' not in variation:
                        _error(str(i), f"Events with {field} variation must specify a distribution")
            if len(agent_errors) > 0:
                continue

            attr_name = f"event_{event['type']}"
            attrs[attr_name] = event['function']
            mag_var = event['magnitude'].get('variation', None)
            dur_var = event['duration'].get('variation', None)
            attr_details[attr_name] = dict(
                scope=event['scope'],
                probability_value=event['probability']['value'],
                probability_unit=event['probability'].get('unit', 'hour'),
                magnitude_value=None if 'magnitude' not in event else event['magnitude']['value'],
                magnitude_variation_upper = None if not mag_var else mag_var.get('upper', 1),
                magnitude_variation_lower = None if not mag_var else mag_var.get('lower', 1),
                magnitude_variation_distribution = None if not mag_var else mag_var['distribution'],
                duration_value=None if 'duration' not in event else event['duration']['value'],
                duration_unit=None if 'duration' not in event else event['duration'].get('unit', 'hour'),
                duration_variation_upper = None if not dur_var else dur_var.get('upper', 1),
                duration_variation_lower = None if not dur_var else dur_var.get('lower', 1),
                duration_variation_distribution = None if not dur_var else dur_var['distribution'],
            )
            agents_data[agent] = dict(attributes=attrs, attribute_details=attr_details)
            if len(agent_errors) > 0:
                agents_errors[agent] = agent_errors
    return agents_data, agents_errors

def merge_json(default, user):
    """Recursively merge a default data_file object with user data"""
    if isinstance(user, dict):
        for field, values in user.items():
            if field in default:
                default[field] = merge_json(default[field], values)
            else:
                default[field] = values
        return default
    elif isinstance(user, list):
        # There are three possible cases for lists:
        # 1. If list elements don't have a 'type' attribute, just concatinate
        #    the lists (e.g. connections in agent_conn.json)
        if 'type' not in user[0]:
            return default + user
        merged = []
        used_types = set([])
        for item in user:
            match = next((d for d in default if d['type'] == item['type']), None)
            if match is not None:
                # 2. If the 'type' in user element matches a default element,
                #    merge the two (e.g. inputs/outputs in agent_desc.json)
                used_types.add(match['type'])
                merged.append(merge_json(match, item))
            else:
                # 3. Else, add a new item to the list (e.g. characteristics
                #    in agent_desc.json)
                merged.append(item)
        for item in default:
            if item['type'] not in used_types:
                merged.append(item)
        return merged
    elif isinstance(user, (str, int, float, bool)):
        return user
