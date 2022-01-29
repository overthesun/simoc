import json
import pytest
from pytest import approx

from simoc_server import front_end_routes

eclss_agents = [
    'solid_waste_aerobic_bioreactor', 'multifiltration_purifier_post_treatment',
    'oxygen_generation_SFWE', 'urine_recycling_processor_VCD',
    'co2_removal_SAWD', 'co2_makeup_valve', 'co2_storage',
    'co2_reduction_sabatier', 'ch4_removal_agent', 'dehumidifier'
]

class GameConfig:
    def __init__(self, game_config, save_output=False):
        self.game_config = front_end_routes.convert_configuration(game_config, save_output)

    def __getattr__(self, attrname):
        assert attrname in self.game_config
        if attrname in self.game_config:
            return self.game_config[attrname]

    def check_agent(self, agent_type, id=None, amount=None, currencies=None,
                    in_conn=None, out_conn=None):
        """Tests whether game_config contains details for a particular agent"""
        assert agent_type in self.agents
        agent = self.agents[agent_type]
        if id:
            assert agent['id'] == id
        if amount:
            assert agent['amount'] == amount
        if currencies:
            for curr, expected in currencies.items():
                assert curr in agent
                assert agent[curr] == approx(expected)

# Test basic fields
def test_convert_one_human(one_human):
    gc = GameConfig(one_human)

    # Game Variables
    assert gc.single_agent == 1
    assert len(gc.agents) == 17

    termination = gc.termination
    assert termination[0]['condition'] == 'time'
    assert termination[0]['value'] == 10
    assert termination[0]['unit'] == 'day'

    priorities = gc.priorities
    expected_priorities = ['structures', 'storage', 'power_generation',
                           'inhabitants', 'eclss', 'plants']
    for i, agent_class in enumerate(expected_priorities):
        assert priorities[i] == agent_class

    gc.check_agent('human_agent', amount=1)
    gc.check_agent('solar_pv_array_mars', amount=30)
    gc.check_agent('crew_habitat_small', id=1, amount=1)
    assert 'atmosphere_equalizer' not in gc.agents

    # Storages
    water_curr = dict(potable=900, treated=100, urine=0, feces=0)
    gc.check_agent('water_storage', id=1, amount=1, currencies=water_curr)
    nutrient_curr = dict(fertilizer=300, biomass=0, waste=0)
    gc.check_agent('nutrient_storage', id=1, amount=1, currencies=nutrient_curr)
    gc.check_agent('ration_storage', id=1, amount=1, currencies=dict(ration=100))
    gc.check_agent('power_storage', id=1, amount=1, currencies=dict(kwh=1000))
    assert 'food_storage' not in gc.agents

    # ECLSS
    for agent in eclss_agents:
        gc.check_agent(agent, id=1, amount=1)

# Test with greenhouse and plants
def test_convert_four_humans_garden(four_humans_garden):
    gc = GameConfig(four_humans_garden)

    # Humans
    gc.check_agent('human_agent', amount=4)

    # Structures
    habitat_curr = dict(n2=2205.873, o2=591.7245, co2=1.167629, ch4=0.00528275,
                        h2=0.00155375, h2o=28.25)
    gc.check_agent('crew_habitat_medium', id=1, amount=1, currencies=habitat_curr)
    greenhouse_curr = dict(n2=478.2645, o2=128.29425, co2=0.2531585,
                           ch4=0.001145375, h2=0.000336875, h2o=6.125)
    gc.check_agent('greenhouse_small', id=1, amount=1, currencies=greenhouse_curr)
    gc.check_agent('atmosphere_equalizer', id=1, amount=1)

    # Storages
    gc.check_agent('power_storage', amount=2)
    fs_curr = dict(wheat=0, cabbage=0, strawberry=0, radish=0, red_beet=0, onion=0)
    gc.check_agent('food_storage', id=1, amount=1, currencies=fs_curr)

    # Plants
    garden = dict(wheat=20, cabbage=30, strawberry=10, radish=50, red_beet=50, onion=50)
    for plant, amount in garden.items():
        gc.check_agent(plant, amount=amount)
