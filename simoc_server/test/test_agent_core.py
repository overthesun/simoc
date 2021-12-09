import time
import json
import copy
import random
import datetime

import pytest
from pytest import approx

from simoc_server.front_end_routes import convert_configuration
from simoc_server.agent_model import AgentModel

def test_agent_one_human_radish(one_human_radish):
    one_human_radish_converted = convert_configuration(one_human_radish)
    one_human_radish_converted['agents']['food_storage']['wheat'] = 2
    model = AgentModel.from_config(one_human_radish_converted)
    model.step_to(n_steps=50)
    export_data(model, 'agent_records_baseline.json')
    agent_records = model.get_data(debug=True)

    # Storage
    water_storage = agent_records['water_storage']
    assert water_storage['capacity']['potable']['value'] == 4000
    assert water_storage['capacity']['water']['value'] == 16000
    assert water_storage['storage']['potable'][50] == 1484.7081036234254
    assert water_storage['storage']['urine'][50] == approx(1.523082)
    assert water_storage['storage']['feces'][50] == approx(1.354150)
    assert water_storage['storage']['treated'][50] == approx(1.42)

    food_storage = agent_records['food_storage']
    assert food_storage['capacity']['wheat']['value'] == 10000
    assert food_storage['capacity']['food']['value'] == 220000
    assert food_storage['storage']['wheat'][30] == approx(0.11249)
    assert food_storage['storage']['wheat'][40] == 0

    ration_storage = agent_records['ration_storage']
    assert ration_storage['capacity']['ration']['value'] == 10000
    assert ration_storage['capacity']['food']['value'] == 10000
    assert ration_storage['storage']['ration'][30] == 100
    assert ration_storage['storage']['ration'][40] == approx(99.48332)

    # Growth
    radish_growth = agent_records['radish']['growth']
    assert radish_growth['current_growth'][50] == approx(3.0096386e-06)
    assert radish_growth['growth_rate'][50] == approx(1.0884092e-05)
    assert radish_growth['grown'][50] == False
    assert radish_growth['agent_step_num'][50] == 50

    # Flows
    radish_flows = agent_records['radish']['flows']
    assert radish_flows['co2'][30] == approx(2.721425e-06)
    assert radish_flows['potable'][30] == approx(7.5320653e-06)
    assert radish_flows['fertilizer'][30] == approx(3.77242353e-08)
    assert radish_flows['kwh'][10] == approx(7.251227132)
    assert radish_flows['biomass'][30] == approx(3.6055921e-06)
    assert radish_flows['o2'][30] == approx(1.9695400e-06)
    assert radish_flows['h2o'][30] == approx(6.6478915e-06)
    assert radish_flows['radish'][30] == 0

    # Buffer
    assert agent_records['co2_removal_SAWD']['buffer']['in_co2'][40] == 8
    # Sometimes this value is 2, sometimes it's 1. I think due to a rounding error.
    assert agent_records['co2_removal_SAWD']['buffer']['in_co2'][49] in [1, 2]

def test_agent_disaster(disaster):
    disaster_converted = convert_configuration(disaster)
    model = AgentModel.from_config(disaster_converted)
    model.step_to(n_steps=100)
    export_data(model, 'agent_records_disaster.json')
    agent_records = model.get_data(debug=True)

    # Amount
    radish_amount = agent_records['radish']['amount']
    assert radish_amount[88] == 400
    assert radish_amount[89] == 378
    assert radish_amount[90] == 52
    assert radish_amount[91] == 0

    # Growth
    growth_test={
        'current_growth': [1.7431033e-8, 2.5857127e-8],
        'growth_rate': [6.3037796e-8, 9.3510023e-8],
        'grown': [False, False],
        'agent_step_num': [5.0, 6.0]
    }
    for i, step in enumerate([5, 7]):
        for field, expected_values in growth_test.items():
            assert agent_records['radish']['growth'][field][step] == approx(expected_values[i])

    # Flows
    radish_flows = agent_records['radish']['flows']
    assert radish_flows['co2'][5] == approx(3.6270955e-06)
    assert radish_flows['potable'][5] == approx(1.0038681e-05)
    assert radish_flows['fertilizer'][5] == approx(5.0278583e-08)
    assert radish_flows['kwh'][5] == approx(0)
    assert radish_flows['biomass'][5] == approx(2.7546116e-06)
    assert radish_flows['o2'][5] == approx(2.6249884e-06)
    assert radish_flows['h2o'][5] == approx(8.8602610e-06)
    assert radish_flows['radish'][5] == 0

    # Deprive
    radish_deprive = agent_records['radish']['deprive']
    assert radish_deprive['in_kwh'][5] == 28800
    assert radish_deprive['in_kwh'][50] == 13462
    assert radish_deprive['in_kwh'][95] == -306

def test_agent_four_humans_garden(four_humans_garden):
    four_humans_garden_converted = convert_configuration(four_humans_garden)
    model = AgentModel.from_config(four_humans_garden_converted)
    model.step_to(n_steps=2)
    export_data(model, 'agent_records_fhgarden.json')

def export_data(model, fname):
    agent_records = model.get_data(debug=True)
    for agent in model.scheduler.agents:
        if agent.agent_type not in agent_records:
            continue
        step_values = agent.step_values
        for currency, vals in step_values.items():
            step_values[currency] = vals.tolist()
        agent_records[agent.agent_type]['step_values'] = step_values
    with open('data_analysis/' + fname, 'w') as f:
        json.dump(agent_records, f)
