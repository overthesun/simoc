import time
import json
import copy
import random
import datetime

import pytest

from simoc_server.front_end_routes import convert_configuration
from simoc_server.agent_model import (AgentModel,
                                      AgentModelInitializationParams,
                                      BaseLineAgentInitializerRecipe)

class AgentModelInstance():
    """An individual instance of an Agent Model

    Initializes a new AgentModel and all associated children based on a
    game_config file. Borrows heavily from the GameRunner object in
    game_runner.py.

    """
    def __init__(self, game_config, currencies):
        self.game_config = copy.deepcopy(game_config)
        self.currencies = currencies

        # Setup model records storages
        self.model_records = []
        self.agent_type_counts = []
        self.storage_capacities = []
        self.step_records = []

        # Build model initialization objects
        self.model_init_params = AgentModelInitializationParams()
        self.model_init_params.set_currencies(currencies)
        self.model_init_params.set_grid_width(100) \
            .set_grid_height(100) \
            .set_starting_model_time(datetime.timedelta())
        if 'termination' in game_config:
            self.model_init_params.set_termination(game_config['termination'])
        if 'minutes_per_step' in game_config:
            self.model_init_params.set_minutes_per_step(game_config['minutes_per_step'])
        if 'priorities' in game_config:
            self.model_init_params.set_priorities(game_config['priorities'])
        if 'location' in game_config:
            self.model_init_params.set_location(game_config['location'])
        self.model_init_params.set_config(game_config)
        if 'single_agent' in game_config and game_config['single_agent'] == 1:
            self.model_init_params.set_single_agent(1)
        self.agent_init_recipe = BaseLineAgentInitializerRecipe(game_config)

        # Build the agent model
        self.game_id = random.getrandbits(63)
        self.start_time = int(time.time())
        self.agent_model = AgentModel.create_new(self.model_init_params,
                                                 self.agent_init_recipe)
        self.agent_model.game_id = self.game_id
        self.agent_model.start_time = self.start_time

    def step_to(self, max_step_num):
        """Advances the agent model by max_step_num steps."""
        while self.agent_model.step_num < max_step_num and not self.agent_model.is_terminated:
            self.agent_model.step()
            # Log step data
            model_record, agent_type_counts, storage_capacities = self.agent_model.get_step_logs()
            self.model_records.append(model_record)
            self.agent_type_counts.append(agent_type_counts)
            self.storage_capacities.append(storage_capacities)
        self.step_records.append(self.agent_model.step_records_buffer)

    def all_records(self):
        """Return all records associated with model"""
        return {
            'model_records': self.model_records,
            'agent_type_counts': self.agent_type_counts,
            'storage_capacities': self.storage_capacities,
            'step_records': self.step_records
        }

    def check_agents(self, agent_desc, agent_class_dict):
        """Verify that everything from game_config was added correctly"""
        dir_dict = dict(input='in', output='out')
        storage_agents = [a.agent_type for a in self.agent_model.get_agents_by_role(role="storage")]
        flows_agents = [a.agent_type for a in self.agent_model.get_agents_by_role(role="flows")]
        single_agent = self.game_config.get('single_agent', 0)

        for agent in self.game_config['agents']:
            agent_config_data = self.game_config['agents'][agent]
            # Agents were added to model with correct amount
            amount = 1 if single_agent else agent_config_data.get(amount, 1)
            agent_instances = self.agent_model.get_agents_by_type(agent_type=agent)
            assert len(agent_instances) == amount

            instance = agent_instances[0]
            agent_desc_data = agent_desc[agent_class_dict[agent]][agent]['data']
            for direction in ['input', 'output']:
                if direction in agent_desc_data and len(agent_desc_data[direction]) > 0:
                    assert agent in flows_agents
                    flows = agent_desc_data[direction]
                    for flow in flows:
                        currency = flow['type']
                        prefix = dir_dict[direction]
                        # Inputs and Outputs loaded to Agents
                        attr_name = prefix + '_' + currency
                        assert attr_name in instance['attrs']
                        # No duliicate connections
                        instance_connections = [a.agent_type for a in instance.selected_storage[prefix][currency]]
                        assert len(instance_connections) == len(set(instance_connections))
                        # Connections match config file
                        assert 'connections' in agent_config_data
                        expected_connections = agent_config_data['connections'][prefix][currency]
                        assert expected_connections == instance_connections


            if 'characteristics' in agent_desc_data and len(agent_desc_data['characteristics']) > 0:
                for char in agent_desc_data['characteristics']:
                    # Characteristics are loaded ot agents
                    attr_name = 'char_' + char['type']
                    assert attr_name in instance['attrs']
                    # Storages are loaded to Agents
                    if 'capacity' in char['type']:
                        assert agent in storage_agents


def test_model_one_human(one_human, agent_desc, agent_class_dict, currency_desc):
    one_human_converted = convert_configuration(one_human)
    model = AgentModelInstance(one_human_converted, currency_desc)
    model.check_agents(agent_desc, agent_class_dict)

    model.step_to(5)
    assert model.agent_model.step_num == 5

    currency_classes = model.agent_model.currency_ref.keys()
    assert len(currency_classes) > 1

    # records = model.all_records()
    # with open('one_human_records.json', 'w') as f:
    #     json.dump(records, f)


def test_model_four_humans_garden(four_humans_garden, agent_desc, agent_class_dict, currency_desc):
    four_humans_garden_converted = convert_configuration(four_humans_garden)
    model = AgentModelInstance(four_humans_garden_converted, currency_desc)
    model.check_agents(agent_desc, agent_class_dict)

    model.step_to(5)
    assert model.agent_model.step_num == 5

    # records = model.all_records()
    # with open('four_humans_garden_records.json', 'w') as f:
    #     json.dump(records, f)
