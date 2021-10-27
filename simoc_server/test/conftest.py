import json

import pytest

@pytest.fixture(autouse=True, scope="session")
def agent_desc():
    with open('agent_desc.json') as f:
        yield json.load(f)

@pytest.fixture(autouse=True, scope="session")
def agent_class_dict(agent_desc):
    output = {}
    for agent_class, agents in agent_desc.items():
        for agent in agents:
            output[agent] = agent_class
    return output

@pytest.fixture(autouse=True, scope="session")
def currency_desc():
    with open('data_files/currency_desc.json') as f:
        yield json.load(f)

# Matches the 'One Human' preset
@pytest.fixture()
def one_human():
    return {
        'duration': {'type': 'day', 'value': 10},
        'human_agent': {'amount': 1},
        'food_storage': {'food_edbl': 100},
        'eclss': {'amount': 1},
        'solar_pv_array_mars': {'amount': 30},
        'power_storage': {'enrg_kwh': 1000},
        'nutrient_storage': {'sold_n': 100, 'sold_p': 100, 'sold_k': 100},
        'single_agent': 1,
        'habitat': 'crew_habitat_small',
    }

# Matches the '4 Humans + Garden' preset
@pytest.fixture()
def four_humans_garden():
    return {
        'duration': {'type': 'day', 'value': 100},
        'human_agent': {'amount': 4},
        'food_storage': {'food_edbl': 1200},
        'eclss': {'amount': 1},
        'solar_pv_array_mars': {'amount': 400},
        'power_storage': {'enrg_kwh': 2000},
        'nutrient_storage': {'sold_n': 100, 'sold_p': 100, 'sold_k': 100},
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
