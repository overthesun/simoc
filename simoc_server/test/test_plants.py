import json, copy
import pandas as pd

import pytest

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

@pytest.fixture()
def reference_data():
    df = pd.read_csv('simoc_server/test/plant_data/simoc-plant-exchanges.csv')
    return df

@pytest.mark.parametrize('species', [ 'wheat', 'lettuce', 'orchard' ])
    # 'wheat', 'soybean', 'lettuce', 'white_potato', 'tomato', 'sweet_potato',
    # 'peanut', 'rice', 'dry_bean', 'spinach', 'chard', 'radish', 'red_beet',
    # 'strawberry', 'cabbage', 'carrot', 'celery', 'green_onion', 'onion', 'pea',
    # 'pepper', 'snap_bean', 'sorghum', 'vegetables', 'corn', 'orchard'])
# @pytest.mark.skip(reason="Very time consuming")
def test_plant_growth_values(reference_data, species):

    plant_ref = reference_data.loc[reference_data['plant'] == species]
    ref = lambda field: plant_ref.iloc[0][field]

    # plant, in_co2, in_potable, in_fertilizer, out_o2, out_h2o, out_biomass,
    # char_par_baseline, char_photoperiod, char_lifetime, char_carbon_fixation,
    # char_harvest_index
    lifetime = ref('char_lifetime') * 24

    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)
    del config['agents']['radish']
    del config['termination']
    amount = 10
    config['agents'][species] = {'amount': amount}
    model = AgentModel.from_config(config)
    model.step_to(n_steps=lifetime + 1)

    data = model.get_data()

    # Confirm harvest worked correctly
    expected_food = ref('out_biomass') * lifetime * amount * ref(f'char_harvest_index')
    food_storage = model.get_agents_by_type('food_storage')[0]
    actual_food = food_storage[species]
    assert abs(actual_food - expected_food) / actual_food < .05  # Within 8% of expected

