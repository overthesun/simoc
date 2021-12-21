import json

import pytest
from agent_model.parse_data_files import parse_currency_desc

# Returns the agent_desc.json file as a dict
@pytest.fixture(autouse=True, scope="session")
def agent_desc():
    with open('data_files/agent_desc.json') as f:
        yield json.load(f)

# Returns a dict of {agent:agent_class} pairs
@pytest.fixture(autouse=True, scope="session")
def agent_class_dict(agent_desc):
    output = {}
    for agent_class, agents in agent_desc.items():
        for agent in agents:
            output[agent] = agent_class
    return output

# Returns the currency_desc.json file as a dict of {currency_class:currency} pairs
@pytest.fixture(autouse=True, scope="session")
def currency_desc():
    with open('data_files/currency_desc.json') as f:
        yield json.load(f)

@pytest.fixture(autouse=True, scope="session")
def currency_dict(currency_desc):
    currency_desc, currency_errors = parse_currency_desc(currency_desc)
    return currency_desc

# Matches the 'One Human' preset
@pytest.fixture()
def one_human():
    return {
        'duration': {'type': 'day', 'value': 10},
        'human_agent': {'amount': 1},
        'food_storage': {'ration': 100},
        'eclss': {'amount': 1},
        'solar_pv_array_mars': {'amount': 30},
        'power_storage': {'kwh': 1000},
        'nutrient_storage': {'fertilizer': 300},
        'single_agent': 1,
        'habitat': 'crew_habitat_small',
    }

@pytest.fixture()
def disaster():
    return {
        'duration': {'type': 'day', 'value': 30},
        'food_storage': {'ration': 100},
        'eclss': {'amount': 0},
        'solar_pv_array_mars': {'amount': 10},
        'power_storage': {'kwh': 1},
        'nutrient_storage': {'fertilizer': 300},
        'single_agent': 1,
        'habitat': 'crew_habitat_small',
        'greenhouse': 'greenhouse_small',
        'plants': [{'species': 'radish', 'amount': 400}]
    }

# Matches the 'One Human + Radish' preset
@pytest.fixture()
def one_human_radish():
    return {
        'duration': {'type': 'day', 'value': 30},
        'human_agent': {'amount': 1},
        'food_storage': {'ration': 100},
        'eclss': {'amount': 1},
        'solar_pv_array_mars': {'amount': 70},
        'power_storage': {'kwh': 1000},
        'nutrient_storage': {'fertilizer': 300},
        'single_agent': 1,
        'habitat': 'crew_habitat_small',
        'greenhouse': 'greenhouse_small',
        'plants': [{'species': 'radish', 'amount': 40}]
    }

# Matches the '4 Humans + Garden' preset
@pytest.fixture()
def four_humans_garden():
    return {
        'duration': {'type': 'day', 'value': 100},
        'human_agent': {'amount': 4},
        'food_storage': {'ration': 1200},
        'eclss': {'amount': 1},
        'solar_pv_array_mars': {'amount': 400},
        'power_storage': {'kwh': 2000},
        'nutrient_storage': {'fertilizer': 300},
        'single_agent': 1,
        'greenhouse': 'greenhouse_small',
        'habitat': 'crew_habitat_medium',
        'plants': [
            {'species': 'wheat', 'amount': 20},
            {'species': 'cabbage', 'amount': 30},
            {'species': 'strawberry', 'amount': 10},
            {'species': 'radish', 'amount': 50},
            {'species': 'red_beet', 'amount': 50},
            {'species': 'onion', 'amount': 50}
        ],
    }
