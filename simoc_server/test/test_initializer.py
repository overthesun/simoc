import json

import pytest
from pytest import approx

from simoc_server.agent_model import AgentModelInitializer
from simoc_server.front_end_routes import convert_configuration

def test_initializer_new(one_human):
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
    assert md['currencies']['atmosphere']['type'] == 'currency_class'
    assert md['currencies']['o2']['class'] == 'atmosphere'

    ad = initializer.agent_data
    assert len(ad) == 17
    assert ad['human_agent']['agent_desc']['agent_class'] == 'inhabitants'
    assert ad['human_agent']['instance']['amount'] == 1

