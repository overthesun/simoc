import json

import pytest

import pandas as pd

"""
APPROACH:

For each plant:
1. Load the standard one_human_radish config
2. Replace radish with plant
3. Load reference data from .csv
4. Run sim length of one lifetime, assert mean exchanges match reference data
5. Run with limited light and decreased co2, assert changes as expected

"""

from agent_model import AgentModel
from agent_model.util import parse_data

@pytest.fixture()
def reference_data():
    df = pd.read_csv('simoc_server/test/plant_data/simoc-plant-exchanges.csv')
    return df

@pytest.mark.parametrize('species', #['wheat', 'lettuce', 'orchard'])
    ['wheat', 'soybean', 'lettuce', 'white_potato', 'tomato', 'sweet_potato',
     'peanut', 'rice', 'dry_bean', 'spinach', 'chard', 'radish', 'red_beet',
     'strawberry', 'cabbage', 'carrot', 'celery', 'green_onion', 'onion', 'pea',
     'pepper', 'snap_bean', 'sorghum', 'vegetables', 'corn', 'orchard'])
@pytest.mark.parametrize('food_tolerance', [0.07])      # within 7%
@pytest.mark.parametrize('exchange_tolerance', [0.01])  # within 1%
def test_plant_growth_values(reference_data, species,
                             food_tolerance,
                             exchange_tolerance):

    species_index = ' '.join(species.split('_'))
    plant_ref = reference_data.loc[reference_data['plant'] == species_index]
    ref = lambda field: plant_ref.iloc[0][field]
    lifetime = ref('char_lifetime') * 24

    # Generate a configuration from 1 human + radish
    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)
    del config['agents']['radish']
    del config['termination']
    amount = 10
    config['agents'][species] = {'amount': amount}

    # Require adjustments to make all plants pass
    config['agents']['multifiltration_purifier_post_treatment'] = {'amount': 3}
    config['agents']['solar_pv_array_mars']['amount'] = 200
    config['agents']['co2_storage']['co2'] = 200
    config['agents']['greenhouse_small']['co2'] *= 10

    # Run at higher CO2 to ensure full growth
    user_agent_desc = {
        'eclss': {
            'co2_removal_SAWD': {'data': {'input': [{'type': 'co2', 'criteria': {'value': 2500}}]}},
            'co2_makeup_valve': {'data': {'input': [{'type': 'co2', 'criteria': {'value': 2000}}]}},
        }
    }

    model = AgentModel.from_config(config, agent_desc=user_agent_desc)
    model.step_to(n_steps=lifetime + 1)

    # Check total food produced
    actual_food = model.get_agents_by_type('food_storage')[0][species]
    expected_food = (ref('out_biomass') * lifetime * amount *
                     ref(f'char_harvest_index'))
    off_by = abs(actual_food - expected_food) / actual_food
    assert off_by < food_tolerance

    # Check all currency exchanges
    data = model.get_data()
    exchanges = ['in_co2', 'in_potable', 'in_fertilizer', 'out_o2', 'out_h2o',
                 'out_biomass']
    for exchange in exchanges:
        direction, currency = exchange.split('_')
        path = [species, 'flows', direction, currency, 'SUM', '*']
        all_flows = parse_data(data, path)
        actual_exchange = sum(all_flows) / len(all_flows)
        expected_exchange = ref(exchange) * amount
        off_by = abs(actual_exchange - expected_exchange) / actual_exchange
        assert off_by < exchange_tolerance, f'{currency} exchange off by {off_by}'
