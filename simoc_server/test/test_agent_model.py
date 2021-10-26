import datetime
import time
import random
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
    def __init__(self, game_config):

        # Setup model records storages
        self.model_records = []
        self.agent_type_counts = []
        self.storage_capacities = []
        self.step_records = []

        # Build model initialization objects
        self.model_init_params = AgentModelInitializationParams()
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

    def step_to(self, max_step_num, buffer_size=10):
        model_records_buffer = []
        agent_type_counts_buffer = []
        storage_capacities_buffer = []
        while self.agent_model.step_num <= max_step_num and not self.agent_model.is_terminated:
            self.agent_model.step()
            model_record, agent_type_counts, storage_capacities = self.agent_model.get_step_logs()
            model_records_buffer.append(model_record)
            agent_type_counts_buffer += agent_type_counts
            storage_capacities_buffer += storage_capacities
            if self.agent_model.step_num % buffer_size == 0:
                self.save_records(model_records_buffer,
                                  agent_type_counts_buffer,
                                  storage_capacities_buffer,
                                  self.agent_model.step_records_buffer)
                model_records_buffer = []
                agent_type_counts_buffer = []
                storage_capacities_buffer = []
                self.agent_model.step_records_buffer = []
        self.save_records(model_records_buffer,
                          agent_type_counts_buffer,
                          storage_capacities_buffer,
                          self.agent_model.step_records_buffer)

    def save_records(self, model_records, agent_type_counts, storage_capacities, step_records):
        self.model_records.append(model_records)
        self.agent_type_counts.append(agent_type_counts)
        self.storage_capacities.append(storage_capacities)
        self.step_records.append(step_records)

def test_model_one_human(one_human):
    one_human_converted = convert_configuration(one_human)
    model = AgentModelInstance(one_human_converted)
    assert model.agent_model.step_num == 0

def test_model_four_humans_garden(four_humans_garden):
    four_humans_garden_converted = convert_configuration(four_humans_garden)
    model = AgentModelInstance(four_humans_garden_converted)
    assert model.agent_model.step_num == 0


