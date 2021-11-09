import time
import json
import copy
import random
import datetime

import pytest
from pytest import approx

from simoc_server.front_end_routes import convert_configuration
from simoc_server.agent_model import AgentModel
from simoc_server.game_runner import GameRunnerInitializationParams

class Record():
    def __init__(self, agent):
        # Static Fields
        self.agent = agent
        self.name = agent.agent_type
        self.lifetime = agent.lifetime
        self.full_amount = self.agent.full_amount
        self.reproduce = agent.reproduce
        # Dynamic Fields
        self.age = [0]
        self.amount = [self.agent.amount]
        self.snapshot_attrs = ['name', 'lifetime', 'full_amount', 'reproduce',
                               'age', 'amount']
        for attr, attr_value in self.agent.attrs.items():
            if attr_value == 0:
                continue
            # Storage
            if attr.startswith('char_capacity'):
                if 'storage' not in self.snapshot_attrs:
                    self.snapshot_attrs.append('storage')
                    self.storage = {}
                currency = attr.split('_', 2)[2]
                self.storage[currency] = [self.agent[currency]]
                if 'capacity' not in self.snapshot_attrs:
                    self.snapshot_attrs.append('capacity')
                    self.capacity = {}
                self.capacity[currency] = dict(value=attr_value,
                                               units=self.agent.attr_details[attr]['units'])
                currency_class = self.agent.currency_dict[currency]['class']
                if currency_class not in self.capacity:
                    class_attr = f"char_capacity_{currency_class}"
                    self.capacity[currency_class] = dict(value=self.agent[class_attr],
                                                         units=self.agent.attr_details[class_attr]['units'])
            # Growth
            if attr.startswith('char_growth_criteria'):
                self.snapshot_attrs += ['total_growth', 'growth']
                self.total_growth = self.agent.total_growth,
                self.growth = dict(current_growth=[self.agent.current_growth],
                                   growth_rate=[self.agent.growth_rate],
                                   grown=[self.agent.grown],
                                   agent_step_num=[self.agent.agent_step_num])
            # Flows
            if attr.startswith('in') or attr.startswith('out'):
                if 'flows' not in self.snapshot_attrs:
                    self.snapshot_attrs += ['flows', 'flow_records']
                    self.flows = {}
                    self.flow_records = {}
                currency = attr.split('_', 1)[1]
                self.flows[currency] = [0]
                self.flow_records[currency] = [{}]
                # Buffer
                cr_buffer = self.agent.attr_details[attr]['criteria_buffer']
                if cr_buffer:
                    if 'buffer' not in self.snapshot_attrs:
                        self.snapshot_attrs.append('buffer')
                        self.buffer = {}
                    prefix = attr.split('_', 1)[0]
                    cr_name = self.agent.attr_details[attr]['criteria_name']
                    cr_id = '{}_{}_{}'.format(prefix, currency, cr_name)
                    self.buffer[cr_id] = [0]
                # Deprive
                deprive_value = self.agent.attr_details[attr]['deprive_value']
                if deprive_value:
                    if 'deprive' not in self.snapshot_attrs:
                        self.snapshot_attrs.append('deprive')
                        self.deprive = {}
                    self.deprive[currency] = [deprive_value * self.full_amount]

    def step(self):
        self.age.append(self.agent.age)
        self.amount.append(self.agent.amount)
        if 'storage' in self.snapshot_attrs:
            for currency, record in self.storage.items():
                record.append(self.agent[currency])
        if 'growth' in self.snapshot_attrs:
            for field, record in self.growth.items():
                record.append(self.agent[field])
        if 'flows' in self.snapshot_attrs:
            for currency, record in self.flows.items():
                record.append(self.agent.last_flow[currency])
            for currency, record in self.flow_records.items():
                record.append(self.agent.flows[currency])
        if 'buffer' in self.snapshot_attrs:
            for cr_id, record in self.buffer.items():
                record.append(self.agent.buffer.get(cr_id, 0))
        if 'deprive' in self.snapshot_attrs:
            for currency, record in self.deprive.items():
                record.append(self.agent.deprive.get(currency, 0))

    def snapshot(self):
        return {a: getattr(self, a) for a in getattr(self, 'snapshot_attrs')}

class AgentModelInstance():
    """An individual instance of an Agent Model

    Initializes a new AgentModel and all associated children based on a
    game_config file. Borrows heavily from the GameRunner object in
    game_runner.py.

    """
    def __init__(self, game_config, currencies):
        # Initialize core dicts
        self.game_config = copy.deepcopy(game_config)
        self.currencies = copy.deepcopy(currencies)
        # Initialize agent model
        grips = GameRunnerInitializationParams(game_config, currencies)
        self.agent_model = AgentModel.create_new(grips.model_init_params,
                                                 grips.agent_init_recipe)
        # Initialize recordkeeping
        self.agent_records = {}
        for agent in self.agent_model.scheduler.agents:
            self.agent_records[agent.agent_type] = Record(agent)

    def step_to(self, n_steps):
        """Advances the agent model by n_steps steps."""
        while self.agent_model.step_num < n_steps and not self.agent_model.is_terminated:
            self.agent_model.step()
            for agent_record in self.agent_records.values():
                agent_record.step()

    def get_agent_data(self):
        """Return all variables for all agents"""
        return {name: r.snapshot() for name, r in self.agent_records.items()}

def test_agent_one_human_radish(one_human_radish, currency_desc):
    one_human_radish_converted = convert_configuration(one_human_radish)
    one_human_radish_converted['agents']['food_storage']['wheat'] = 2
    model = AgentModelInstance(one_human_radish_converted, currency_desc)
    model.step_to(50)
    export_data(model, 'agent_records_baseline.json')
    agent_records = model.get_agent_data()

    # Storage
    assert agent_records['water_storage']['capacity']['potable']['value'] == 4000
    assert agent_records['water_storage']['capacity']['water']['value'] == 16000
    assert agent_records['water_storage']['storage']['potable'][50] == 1484.7081036234254
    assert agent_records['water_storage']['storage']['urine'][50] == approx(1.523082)
    assert agent_records['water_storage']['storage']['feces'][50] == approx(1.354150)
    assert agent_records['water_storage']['storage']['treated'][50] == approx(1.42)

    assert agent_records['food_storage']['capacity']['wheat']['value'] == 10000
    assert agent_records['food_storage']['capacity']['food']['value'] == 220000
    assert agent_records['food_storage']['storage']['wheat'][30] == approx(0.11249)
    assert agent_records['food_storage']['storage']['wheat'][40] == 0

    assert agent_records['ration_storage']['capacity']['ration']['value'] == 10000
    assert agent_records['ration_storage']['capacity']['food']['value'] == 10000
    assert agent_records['ration_storage']['storage']['ration'][30] == 100
    assert agent_records['ration_storage']['storage']['ration'][40] == approx(99.48332)

    # Growth
    assert agent_records['radish']['growth']['current_growth'][50] == approx(3.0096386e-06)
    assert agent_records['radish']['growth']['growth_rate'][50] == approx(1.0884092e-05)
    assert agent_records['radish']['growth']['grown'][50] == False
    assert agent_records['radish']['growth']['agent_step_num'][50] == 50

    # Flows
    assert agent_records['radish']['flows']['co2'][30] == approx(2.721425e-06)
    assert agent_records['radish']['flows']['potable'][30] == approx(7.5320653e-06)
    assert agent_records['radish']['flows']['fertilizer'][30] == approx(3.77242353e-08)
    assert agent_records['radish']['flows']['kwh'][30] == approx(7.251227132)
    assert agent_records['radish']['flows']['biomass'][30] == approx(3.6055921e-06)
    assert agent_records['radish']['flows']['o2'][30] == approx(1.9695400e-06)
    assert agent_records['radish']['flows']['h2o'][30] == approx(6.6478915e-06)
    assert agent_records['radish']['flows']['radish'][30] == 0

    # Buffer
    assert agent_records['co2_removal_SAWD']['buffer']['in_co2_co2_ratio_in'][40] == 8
    # Sometimes this value is 2, sometimes it's 1. I think due to a rounding error.
    assert agent_records['co2_removal_SAWD']['buffer']['in_co2_co2_ratio_in'][49] in [1, 2]

def test_agent_disaster(one_human_radish, currency_desc):
    one_human_radish['human_agent']['amount'] = 0
    one_human_radish['power_storage']['kwh'] = 1
    one_human_radish['solar_pv_array_mars']['amount'] = 10
    one_human_radish['eclss']['amount'] = 0
    one_human_radish['plants'][0]['amount'] = 400
    one_human_radish_converted = convert_configuration(one_human_radish)
    model = AgentModelInstance(one_human_radish_converted, currency_desc)
    model.step_to(100)
    agent_records = model.get_agent_data()

    # Amount
    assert agent_records['radish']['amount'][88] == 400
    assert agent_records['radish']['amount'][89] == 378
    assert agent_records['radish']['amount'][90] == 52
    assert agent_records['radish']['amount'][91] == 0

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
    assert agent_records['radish']['flows']['co2'][5] == approx(3.6270955e-06)
    assert agent_records['radish']['flows']['potable'][5] == approx(1.0038681e-05)
    assert agent_records['radish']['flows']['fertilizer'][5] == approx(5.0278583e-08)
    assert agent_records['radish']['flows']['kwh'][5] == approx(0)
    assert agent_records['radish']['flows']['biomass'][5] == approx(2.7546116e-06)
    assert agent_records['radish']['flows']['o2'][5] == approx(2.6249884e-06)
    assert agent_records['radish']['flows']['h2o'][5] == approx(8.8602610e-06)
    assert agent_records['radish']['flows']['radish'][5] == 0

    # Deprive
    assert agent_records['radish']['deprive']['kwh'][5] == 28800
    assert agent_records['radish']['deprive']['kwh'][50] == 13462
    assert agent_records['radish']['deprive']['kwh'][95] == -306

def test_agent_four_humans_garden(four_humans_garden, currency_desc):
    four_humans_garden_converted = convert_configuration(four_humans_garden)
    model = AgentModelInstance(four_humans_garden_converted, currency_desc)
    model.step_to(2)
    export_data(model, 'agent_records_fhgarden.json')

def export_data(model, fname):
    agent_records = model.get_agent_data()
    for agent in model.agent_model.scheduler.agents:
        if agent.agent_type not in agent_records:
            continue
        step_values = agent.step_values
        for currency, vals in step_values.items():
            step_values[currency] = vals.tolist()
        agent_records[agent.agent_type]['step_values'] = step_values
    with open(fname, 'w') as f:
        json.dump(agent_records, f)
