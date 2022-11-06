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

@pytest.mark.parametrize('species', ['rice', 'radish', 'orchard'])
def test_plant_species(random_seed, reference_data, species):
    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)
    del config['agents']['radish']
    config['agents'][species] = {'amount': 20}
    config['agents']['light'] = {'amount': 1}

    model = AgentModel.from_config(config)
    model.step_to(n_steps=10)
    data = model.get_data()
    print(data)

    # config['agents']['food_storage']['wheat'] = 2
    # config['seed'] = random_seed
    # model = AgentModel.from_config(one_human_radish_converted, data_collection=True)
    # model.step_to(n_steps=50)
    # export_data(model, 'agent_records_baseline.json')
    # agent_records = model.get_data(debug=True)
