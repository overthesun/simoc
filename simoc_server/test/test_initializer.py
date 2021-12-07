import json

import pytest
from pytest import approx

from simoc_server.agent_model import AgentModel, AgentModelInitializer
from simoc_server.front_end_routes import convert_configuration

def test_initializer_from_new(one_human):
    initializer = AgentModelInitializer.from_new(convert_configuration(one_human))
    # with open('data_analysis/initializer.json', 'w') as f:
    #     json.dump(initializer.serialize(), f)

    md = initializer.model_data
    assert len(md) == 8
    assert md['seed'] > 100
    assert md['single_agent'] == 1
    assert md['termination'][0] == dict(condition='time',
                                        value=10,
                                        unit='day')
    assert md['priorities'] == ['structures', 'storage', 'power_generation',
                                'inhabitants', 'eclss', 'plants']
    assert md['location'] == 'mars'
    assert md['total_amount'] == 17
    assert md['minutes_per_step'] == 60
    assert md['currency_dict']['atmosphere']['type'] == 'currency_class'
    assert md['currency_dict']['o2']['class'] == 'atmosphere'

    ad = initializer.agent_data
    assert len(ad) == 17
    assert ad['human_agent']['agent_desc']['agent_class'] == 'inhabitants'
    assert ad['human_agent']['instance']['amount'] == 1

def test_initializer_save_load(disaster):
    model = AgentModel.new(convert_configuration(disaster))
    model.step_to(n_steps=4)
    # Save to json and create duplicate
    saved = model.save()
    with open('data_analysis/saved_game.json', 'w') as f:
        json.dump(saved, f)
    new_model = AgentModel.load(saved)
    resaved = new_model.save()
    with open('data_analysis/resaved_game.json', 'w') as f:
        json.dump(resaved, f)
    # Clear data from both so output is the same
    model.get_data(clear_cache=True)
    new_model.get_data(clear_cache=True)

    model.step_to(n_steps=10)
    new_model.step_to(n_steps=10)

    # Recursively compare all fields
    model_records = model.get_data(debug=True)
    new_model_records = new_model.get_data(debug=True)
    for name, recs in {'original': model_records, 'copied': new_model_records}.items():
        with open(f"data_analysis/save_data_{name}.json", 'w') as f:
            json.dump(recs, f)

    def _compare(a, b):
        if type(a) in [str, int, float]:
            assert a == b
        elif type(a) == dict:
            for k, v in a.items():
                if k not in ['buffer', 'storage_ratios', 'deprive']:
                    _compare(v, b[k])
        elif type(a) == list:
            for i, v in enumerate(a):
                assert v == b[i]

    _compare(model_records, new_model_records)
