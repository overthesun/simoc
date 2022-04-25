import time
import json
import copy
import random
import datetime

import pytest
from pytest import approx

from simoc_server.front_end_routes import convert_configuration
from agent_model import AgentModel

def test_agent_one_human_radish(one_human_radish, random_seed):
    one_human_radish_converted = convert_configuration(one_human_radish)
    # export_config(one_human_radish_converted, 'config_1hrad.json')
    one_human_radish_converted['agents']['food_storage']['wheat'] = 2
    one_human_radish_converted['seed'] = random_seed
    model = AgentModel.from_config(one_human_radish_converted, data_collection=True)
    model.step_to(n_steps=50)
    export_data(model, 'agent_records_baseline.json')
    agent_records = model.get_data(debug=True)

    # Storage
    water_storage = agent_records['water_storage']
    assert water_storage['capacity']['potable']['value'] == 4000
    assert water_storage['capacity']['water']['value'] == 16000
    assert water_storage['storage']['potable'][50] == 1490.8956036234226
    assert water_storage['storage']['urine'][50] == approx(1.041649)
    assert water_storage['storage']['feces'][50] == approx(0.250)
    assert water_storage['storage']['treated'][50] == approx(2.21)

    food_storage = agent_records['food_storage']
    assert food_storage['capacity']['wheat']['value'] == 10000
    assert food_storage['capacity']['food']['value'] == 220000
    assert food_storage['storage']['wheat'][30] == approx(0.05000)
    assert food_storage['storage']['wheat'][40] == 0

    ration_storage = agent_records['ration_storage']
    assert ration_storage['capacity']['ration']['value'] == 10000
    assert ration_storage['capacity']['food']['value'] == 10000
    assert ration_storage['storage']['ration'][30] == 100
    assert ration_storage['storage']['ration'][40] == approx(99.4)

    # Growth
    radish_growth = agent_records['radish']['growth']
    assert radish_growth['current_growth'][50] == approx(3.0096386e-06)
    assert radish_growth['growth_rate'][50] == approx(1.0884093e-05)
    assert radish_growth['grown'][50] == False
    assert radish_growth['agent_step_num'][50] == 50

    # Flows
    radish_flows = agent_records['radish']['flows']
    assert radish_flows['co2'][30] == approx(2.7214252e-06)
    assert radish_flows['potable'][30] == approx(7.5320653e-06)
    assert radish_flows['fertilizer'][30] == approx(3.7724235e-08)
    assert radish_flows['kwh'][10] == approx(7.251227132)
    assert radish_flows['biomass'][30] == approx(3.6055921e-06)
    assert radish_flows['o2'][30] == approx(1.96954003e-06)
    assert radish_flows['h2o'][30] == approx(6.6478915e-06)
    assert radish_flows['radish'][30] == 0

    # Buffer
    assert agent_records['co2_removal_SAWD']['buffer']['in_co2'][40] == 0
    assert agent_records['co2_removal_SAWD']['buffer']['in_co2'][41] == 1


def test_agent_disaster(disaster, random_seed):
    disaster_converted = convert_configuration(disaster)
    # export_config(disaster_converted, 'config_disaster.json')
    disaster_converted['seed'] = random_seed
    model = AgentModel.from_config(disaster_converted, data_collection=True)
    model.step_to(n_steps=100)
    export_data(model, 'agent_records_disaster.json')
    agent_records = model.get_data(debug=True)

    # Amount
    radish_amount = agent_records['radish']['amount']
    assert radish_amount[79] == 400
    assert radish_amount[80] == 64
    assert radish_amount[81] == 16

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
    assert radish_deprive['in_kwh'][50] == 11501
    assert radish_deprive['in_kwh'][95] == 316


def test_agent_four_humans_garden(four_humans_garden):
    four_humans_garden_converted = convert_configuration(four_humans_garden)
    # export_config(four_humans_garden_converted, 'config_4hg.json')
    model = AgentModel.from_config(four_humans_garden_converted, data_collection=True)
    model.step_to(n_steps=2)
    # export_data(model, 'agent_records_fhgarden.json')


def test_agent_variation(one_human_radish, random_seed):
    one_human_radish_converted = convert_configuration(one_human_radish)
    one_human_radish_converted['global_entropy'] = 0.5
    one_human_radish_converted['seed'] = random_seed
    model = AgentModel.from_config(one_human_radish_converted, data_collection=True)

    # with open('data_analysis/agent_variation_save.json', 'w') as f:
    #     json.dump(model.save(), f)
    assert model.global_entropy == 0.5
    assert model.seed == random_seed
    assert model.random_state.rand(1)[0] == 0.65641118308227

    model.step_to(n_steps=10)
    agent_records = model.get_data(debug=True)
    export_data(model, 'agent_records_variable.json')
    def _check_flows(agent, currency, step_9, step_10):
        assert agent_records[agent]['flows'][currency][9] == step_9
        assert agent_records[agent]['flows'][currency][10] == step_10

    human = model.get_agents_by_type('human_agent')[0]
    assert human.initial_variable == 0.9379673759137234
    assert human.attrs['in_o2'] == 0.03635932740740949
    assert human.attrs['in_potable'] == 0.13447248108057724
    assert human.attrs['in_food'] == 0.06365593913392265
    assert human.attrs['out_co2'] == 0.04412118381456972
    assert human.attrs['out_h2o'] == 0.12453350177471556
    assert human.attrs['out_urine'] == 0.060833
    assert human.attrs['out_feces'] == 0.005
    assert human.attrs['char_mass'] == 80.26308652558426

    # s_var = human.step_variable
    # assert human.last_flow['o2'] == human.attrs['in_o2'] * h_var * s_var

    dehumidifier = model.get_agents_by_type('dehumidifier')[0]
    d_var = 0.9885233739822509
    assert dehumidifier.initial_variable == d_var
    assert dehumidifier.attrs['in_h2o'] == d_var * 4
    assert dehumidifier.attrs['in_kwh'] == d_var * 0.5
    assert dehumidifier.attrs['out_treated'] == d_var * 4

    radish = model.get_agents_by_type('radish')[0]
    r_var = 0.9866809472733392
    assert radish.initial_variable == r_var
    assert radish.attrs['in_co2'] == r_var * 0.0007452059028
    assert radish.attrs['in_potable'] == r_var * 0.0020625
    assert radish.attrs['in_fertilizer'] == r_var * 1.033e-05
    assert radish.attrs['in_kwh'] == r_var * 0.1812806783
    assert radish.attrs['in_biomass'] == r_var * 1
    assert radish.attrs['out_o2'] == r_var * 0.0005393177194
    assert radish.attrs['out_h2o'] == r_var * 0.0018203873194
    assert radish.attrs['out_radish'] == r_var * 0.5
    assert radish.attrs['out_inedible_biomass'] == r_var * 0.5

    solar = model.get_agents_by_type('solar_pv_array_mars')[0]
    s_var = 1.003991194483813
    assert solar.initial_variable == s_var
    assert solar.attrs['out_kwh'] == s_var * 0.354

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

def export_config(config, fname):
    with open('data_analysis/' + fname, 'w') as f:
        json.dump(config, f)
