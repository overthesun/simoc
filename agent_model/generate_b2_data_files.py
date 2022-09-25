
import json, copy, sys
from collections import defaultdict

import numpy as np
import pandas as pd

sys.path.insert(0, 'agent_model')
from util import calc_air_storage, calc_water_storage

data_files_path = './data_files/'

# Dates / General
mission_1a_start_date = '1991-09-26'
mission_1b_start_date = '1993-01-12'  # Day 475, pure O2 added
mission_1_end_date = '1993-09-25'  # 730 Days
mission_1_crew_size = 8

mission_2_start_date = '1994-03-06'
mission_2_end_date = '1994-09-06'
mission_2_end_date_original = '1995-01-06'
mission_2_crew_size = 7

def generate_agent_desc():
    """Return a custom agent_desc for SIMOC-B2 based on the original

    Documentation: https://simoc.space/docs/user_guide/api/data-objects.html#agent-description
    """

    # Import all agents from base SIMOC
    agent_desc = None
    with open(data_files_path + 'agent_desc.json') as f:
        agent_desc = json.load(f)

    # Copy existing agents as placeholders where relevant
    _ = lambda _class, _agent: copy.deepcopy(agent_desc[_class][_agent])
    b2_agent_desc = {
        'inhabitants': {
            'human_agent': _('inhabitants', 'human_agent'),
        },
        'eclss': {
            'co2_removal': _('eclss', 'co2_removal_SAWD'),
            'o2_makeup_valve': {},  # Add manually below
        },
        'plants': {
            'rice': _('plants', 'rice'),
            'wheat': _('plants', 'wheat'),
    #         'sorghum': _('plants', 'rice'),  # Placeholder
            'sweet_potato': _('plants', 'sweet_potato'),
    #         'vegetables': _('plants', 'carrot'),  # Placeholder
            'soybean': _('plants', 'soybean'),
            'peanut': _('plants', 'peanut'),
    #         'corn': _('plants', 'rice'),  # Placeholder
            'dry_bean': _('plants', 'dry_bean'),
    #         'orchard': _('plants', 'strawberry'),  # Placeholder
        },
        'structures': {
            'b2_greenhouse': _('structures', 'greenhouse_large'),
            'b2_crew_habitat': _('structures', 'crew_habitat_large'),
            'b2_biomes': _('structures', 'crew_habitat_large'),  # so equalizer recognized as 'habitat'
            'atm_eq_gh_crew': _('structures', 'atmosphere_equalizer'),
            'atm_eq_gh_biomes': _('structures', 'atmosphere_equalizer'),
            'soil': {},  # Add manually below
            'concrete': {},  # Add manually below
        },
        'storage': {
            'water_storage': _('storage', 'water_storage'),
            'food_storage': _('storage', 'food_storage'),
            'nutrient_storage': _('storage', 'nutrient_storage'),
            'co2_storage': _('storage', 'co2_storage'),  # Add manually below
            'o2_storage': {},  # Add manually below
        }
    }

    # Remove all kwh exchanges (v1 of SIMOC-B2 does not include electricity)
    to_remove = []  # Make a list of tuples of paths to all kwh exchanges
    for agent_class, agents in b2_agent_desc.items():
        for agent, agent_data in agents.items():
            if 'data' not in agent_data:
                continue
            for direction in ('input', 'output'):
                for i, exchange in enumerate(agent_data['data'][direction]):
                    if exchange['type'] == 'kwh':
                        to_remove.append((agent_class, agent, direction, i))
    for (agent_class, agent, direction, i) in to_remove:  # Delete one-by-one
        # There would be max one kwh exchange per direction, so this is safe
        del b2_agent_desc[agent_class][agent]['data'][direction][i]

    # Soil
    b2_agent_desc['structures']['soil'] = {
        'description': '1 m^3 of respirating organic soil.',
        'data': {
            "input": [{
                "type": "o2",
                "value": 0.037083,
                "flow_rate": {"unit": "kg", "time": "hour"},
            }],
            "output": [{
                "type": "co2",
                "value": 0.045,
                "flow_rate": {"unit": "kg", "time": "hour"},
            }],
            "characteristics": [
                {"type": "volume", "value": 1, "unit": "m^3"}]}}

    # Concrete
    b2_agent_desc['structures']['concrete'] = {
        'description': '1 m^3 of calcifying concrete of a specified age',
        'data': {
            "input": [{
                "type": "co2",
                "value": 0.05,
                "flow_rate": {"unit": "kg", "time": "hour"},
                "growth": {
                    "lifetime": {
                        "type": "linear",
                    }
                }
            }],
            "output": [],
            "characteristics": [
                {"type": "volume", "value": 1, "unit": "m^3"},
                {"type": "age_at_start", "value": 0, "unit": "hour"}]}}

    # O2 Resupply System
    b2_agent_desc['eclss']['o2_makeup_valve'] = {
        'description': 'Release o2 into atmosphere when it drops below 20%',
        "data": {
            "input": [{
                "type": "o2",
                "value": 0.085,
                "required": "mandatory",
                "flow_rate": {"unit": "kg", "time": "hour"},
                "criteria": {
                    "name": "o2_ratio_out",
                    "limit": "<",
                    "value": 0.2,
                    "buffer": 8}
            }],
            "output": [{
                "type": "o2",
                "value": 0.085,
                "required": "mandatory",
                "requires": ["o2"],
                "flow_rate": {"unit": "kg", "time": "hour"},
            }],
            "characteristics": []}}
    b2_agent_desc['storage']['o2_storage'] = {
        "description": "Store o2 resupply, released via makeup valve",
        "data": {
            "input": [],
            "output": [],
            "characteristics": [{
                "type": "capacity_o2",
                "value": 10000,
                "unit": "kg"}]}}

    # Add food_storage capacity for all plants
    chars = b2_agent_desc['storage']['food_storage']['data']['characteristics']
    chars = [c for c in chars if not c['type'].startswith('capacity')]
    for plant in b2_agent_desc['plants']:
        chars.append({
            'type': f'capacity_{plant}',
            'value': 10_000,
            'unit': 'kg'})
    b2_agent_desc['storage']['food_storage']['data']['characteristics'] = chars
    return b2_agent_desc


def generate_currency_desc(b2_agent_desc):
    """Return a currency_desc for SIMOC-B2 based on the original and the
    SIMOC-B2 agent_desc

    Documenation: https://simoc.space/docs/user_guide/api/data-objects.html#currency-description
    """

    # Load the default currency_desc
    currency_desc = None
    with open(data_files_path + 'currency_desc.json') as f:
        currency_desc = json.load(f)

    # Make a set of the currencies used by b2 agents
    required_currencies = set()
    for agents_of_class in b2_agent_desc.values():
        for agent_data in agents_of_class.values():
            if 'data' not in agent_data:
                continue
            for direction in ('input', 'output'):
                for exchange in agent_data['data'][direction]:
                    if exchange['type'] in currency_desc:
                        continue  # Ignore currency class exchanges
                    required_currencies.add(exchange['type'])

    # Maually add some legacy currencies
    required_currencies.update(('n2', 'h2', 'ch4', 'treated', 'waste'))

    # Copy relevant currencies from default currency_desc
    b2_currency_desc = defaultdict(dict)
    for curr_class, currencies in currency_desc.items():
        for curr, cdata in currencies.items():
            if curr in required_currencies:
                b2_currency_desc[curr_class][curr] = cdata
    b2_currency_desc = dict(b2_currency_desc)

    # Check for missing currencies
    found_currencies = set()
    for currencies in b2_currency_desc.values():
        found_currencies.update(c for c in currencies)
    missing = required_currencies.difference(found_currencies)
    if len(missing) > 0:
        raise ValueError('Missing currency desc for', missing)

    return b2_currency_desc


def generate_agent_conn(b2_agent_desc):
    b2_agent_conn = [
        # Humans
        {'from': 'b2_crew_habitat.o2', 'to': 'human_agent.o2'},
        {'from': 'water_storage.potable', 'to': 'human_agent.potable'},
        {'from': 'food_storage.food', 'to': 'human_agent.food'},
        {'from': 'human_agent.co2', 'to': 'b2_crew_habitat.co2'},
        {'from': 'human_agent.h2o', 'to': 'b2_crew_habitat.h2o'},
        {'from': 'human_agent.urine', 'to': 'water_storage.urine'},
        {'from': 'human_agent.feces', 'to': 'water_storage.feces'},

        # ECLSS
        {'from': 'b2_greenhouse.co2', 'to': 'co2_removal.co2'},
        {'from': 'co2_removal.co2', 'to': 'co2_storage.co2'},
        {'from': 'o2_storage.o2', 'to': 'o2_makeup_valve.o2'},
        {'from': 'o2_makeup_valve.o2', 'to': 'b2_greenhouse.o2'},
    ]

    # Plants
    for plant in b2_agent_desc['plants']:
        # Plants
        b2_agent_conn += [
        {"from": "b2_greenhouse.co2", "to": f"{plant}.co2"},
        {"from": "water_storage.potable", "to": f"{plant}.potable"},
        {"from": "nutrient_storage.fertilizer", "to": f"{plant}.fertilizer"},
        {"from": f"{plant}.biomass", "to": f"{plant}.biomass"},
        {"from": f"{plant}.inedible_biomass", "to": "nutrient_storage.inedible_biomass"},
        {"from": f"{plant}.o2", "to": "b2_greenhouse.o2"},
        {"from": f"{plant}.h2o", "to": "b2_greenhouse.h2o"},
        {"from": f"{plant}.{plant}", "to": f"food_storage.{plant}"},
        ]

    # Structures
    for equalizer, connection in zip(('atm_eq_gh_crew', 'atm_eq_gh_biomes'),
                                    ('b2_crew_habitat', 'b2_biomes')):
        b2_agent_conn += [
            {'from': 'b2_greenhouse.atmosphere', 'to': f'{equalizer}.atmosphere'},
            {'from': f'{connection}.atmosphere', 'to': f'{equalizer}.atmosphere'},
            {'from': f'{equalizer}.atmosphere', 'to': 'b2_greenhouse.atmosphere'},
            {'from': f'{equalizer}.atmosphere', 'to': f'{connection}.atmosphere'},
        ]
    b2_agent_conn += [
        {'from': 'b2_greenhouse.co2', 'to': 'concrete.co2'},
        {'from': 'concrete.o2', 'to': 'b2_greenhouse.o2'},
        {'from': 'b2_greenhouse.o2', 'to': 'soil.o2'},
        {'from': 'soil.co2', 'to': 'b2_greenhouse.co2'},
    ]

    return b2_agent_conn


def generate_config(b2_agent_desc):
    """Return configuration files for the 3 SIMOC-B2 missions: 1a, 1b and c

    Documentation: https://simoc.space/docs/user_guide/api/data-objects.html#config
    """

    def volume(target):
        """Helper function to return volume from agent_desc for agent"""
        for agents_by_class in b2_agent_desc.values():
            for agent, agent_data in agents_by_class.items():
                if agent == target:
                    for char in agent_data['data']['characteristics']:
                        if char['type'] == 'volume':
                            return char['value']

    base_config = {
        # Default fields
        'priorities': ['structures', 'storage', 'inhabitants', 'eclss', 'plants'],
        'seed': 12345,
        'global_entropy': 0,
        'location': 'earth',
        'minutes_per_step': 60,
        'single_agent': 1,

        # Adjustable Fields
        'termination': [{'condition': 'time', 'value': 365, 'unit': 'day',}],
        'agents': {

            # Inhabitants
            'human_agent': {'amount': 1},
            'soil': {'amount': 1},

            # ECLSS
            'co2_removal': {'amount': 1},
            'o2_makeup_valve': {'amount': 1},

            # Plants
            'rice': {'amount': 80},
            'wheat': {'amount': 80},
    #         'sorghum': {'amount': 80},
            'sweet_potato': {'amount': 80},
    #         'vegetables': {'amount': 80},
            'soybean': {'amount': 80},
            'peanut': {'amount': 80},
    #         'corn': {'amount': 80},
            'dry_bean': {'amount': 80},
    #         'orchard': {'amount': 80},

            # Structures
            'b2_greenhouse': calc_air_storage(volume('b2_greenhouse')),
            'b2_crew_habitat': calc_air_storage(volume('b2_crew_habitat')),
            'b2_biomes': calc_air_storage(volume('b2_biomes')),
            'atm_eq_gh_crew': {'amount': 1},
            'atm_eq_gh_biomes': {'amount': 1},
            'concrete': {'amount': 1},

            # Storage
            'water_storage': calc_water_storage(volume('water_storage')),
            'nutrient_storage': {'amount': 1, "fertilizer": 10_000},
            'food_storage': {plant: 50 for plant in b2_agent_desc['plants']},
            'co2_storage': {},
            'o2_storage': {'o2': 2_000},
        }
    }

    mission_1a_days = pd.date_range(mission_1a_start_date,
                                    mission_1b_start_date, freq='D').shape[0]
    mission_1a_config = {
        **base_config,
        'termination': [{'condition': 'time', 'value': mission_1a_days, 'unit': 'day',}],
    }

    mission_1b_days = pd.date_range(mission_1b_start_date,
                                    mission_1_end_date, freq='D').shape[0]
    mission_1b_config = {
        **base_config,
        'termination': [{'condition': 'time', 'value': mission_1b_days, 'unit': 'day',}],
    }

    mission_2_days = pd.date_range(mission_2_start_date,
                                   mission_2_end_date, freq='D').shape[0]
    mission_2_config = {
        **base_config,
        'termination': [{'condition': 'time', 'value': mission_2_days, 'unit': 'day',}],
    }

    return mission_1a_config, mission_1b_config, mission_2_config


if __name__ == '__main__':
    b2_agent_desc = generate_agent_desc()
    b2_currency_desc = generate_currency_desc(b2_agent_desc)
    b2_agent_conn = generate_agent_conn(b2_agent_desc)
    configs = generate_config(b2_agent_desc)
    mission_1a_config, mission_1b_config, mission_2_config = configs

    for item, name in [
        (b2_agent_desc, 'agent_desc'),
        (b2_currency_desc, 'currency_desc'),
        (b2_agent_conn, 'agent_conn'),
        (mission_1a_config, 'config_mission_1a'),
        (mission_1b_config, 'config_mission_1b'),
        (mission_2_config, 'config_mission_2')]:
        with open(data_files_path + f'b2/{name}.json', 'w') as f:
            json.dump(item, f)
            