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
        if in_conn:
            for curr, conns in in_conn.items():
                assert curr in agent['connections']['in']
                for conn in conns:
                    assert conn in agent['connections']['in'][curr]
        if out_conn:
            for curr, conns in out_conn.items():
                assert curr in agent['connections']['out']
                for conn in conns:
                    assert conn in agent['connections']['out'][curr]

    def check_connections(self, agent_desc, agent_class_dict):
        """Tests that each input/output specified in agent_desc has an
           associated connection"""
        dir_dict = dict(input="in", output="out")
        for agent in self.agents:
            # Agent exists in agent_desc
            assert agent in agent_class_dict
            assert agent in agent_desc[agent_class_dict[agent]]

            agent_data = agent_desc[agent_class_dict[agent]][agent]['data']
            agent_connections = self.game_config['agents'][agent]['connections']
            for direction in ['input', 'output']:
                if direction not in agent_data:
                    continue
                for flow in agent_data[direction]:
                    # Each flow has a connection
                    currency = flow['type']
                    dir = dir_dict[direction]
                    assert currency in agent_connections[dir]
                    connections = agent_connections[dir][currency]
                    assert len(connections) > 0
                    # Connections are all to active agents
                    for conn in connections:
                        assert conn in self.agents

# Test basic fields
def test_convert_one_human(one_human, agent_desc, agent_class_dict):
    gc = GameConfig(one_human)

    # Game Variables
    assert gc.single_agent == 1
    assert gc.total_amount == 17

    termination = gc.termination
    assert termination[0]['condition'] == 'time'
    assert termination[0]['value'] == 10
    assert termination[0]['unit'] == 'day'

    priorities = gc.priorities
    expected_priorities = ['structures', 'storage', 'power_generation',
                           'inhabitants', 'eclss', 'plants']
    for i, agent_class in enumerate(expected_priorities):
        assert priorities[i] == agent_class

    # Connections
    gc.check_connections(agent_desc, agent_class_dict)

    # Humans
    human_in = dict(atmo_o2=['crew_habitat_small'], h2o_potb=['water_storage'],
                    food_edbl=['food_storage'])
    human_out = dict(atmo_co2=['crew_habitat_small'], atmo_h2o=['crew_habitat_small'],
                     h2o_urin=['water_storage'], h2o_wste=['water_storage'])
    gc.check_agent('human_agent', amount=1, in_conn=human_in, out_conn=human_out)

    # Solar
    solar_out = dict(enrg_kwh=['power_storage'])
    gc.check_agent('solar_pv_array_mars', amount=30, out_conn=solar_out)

    # Structures
    gc.check_agent('crew_habitat_small', id=1, amount=1)
    assert 'atmosphere_equalizer' not in gc.agents

    # Storages
    water_curr = dict(h2o_potb=900, h2o_tret=100, h2o_urin=0, h2o_wste=0)
    gc.check_agent('water_storage', id=1, amount=1, currencies=water_curr)
    nutrient_curr = dict(sold_n=100, sold_p=100, sold_k=100, biomass_totl=0,
                         biomass_edible=0, sold_wste=0)
    gc.check_agent('nutrient_storage', id=1, amount=1, currencies=nutrient_curr)
    gc.check_agent('food_storage', id=1, amount=1, currencies=dict(food_edbl=100))
    gc.check_agent('power_storage', id=1, amount=1, currencies=dict(enrg_kwh=1000))

    # ECLSS
    for agent in eclss_agents:
        gc.check_agent(agent, id=1, amount=1)

# Test with greenhouse and plants
def test_convert_four_humans_garden(four_humans_garden, agent_desc, agent_class_dict):
    gc = GameConfig(four_humans_garden)

    # Connections
    gc.check_connections(agent_desc, agent_class_dict)

    # Structures
    habitat_curr = dict(atmo_n2=2205.873, atmo_o2=591.7245, atmo_co2=1.167629,
                        atmo_ch4=0.00528275, atmo_h2=0.00155375, atmo_h2o=28.25)
    gc.check_agent('crew_habitat_medium', id=1, amount=1, currencies=habitat_curr)
    greenhouse_curr = dict(atmo_n2=478.2645, atmo_o2=128.29425, atmo_co2=0.2531585,
                           atmo_ch4=0.001145375, atmo_h2=0.000336875, atmo_h2o=6.125)
    gc.check_agent('greenhouse_small', id=1, amount=1, currencies=greenhouse_curr)
    eq_conn = dict(atmo=['crew_habitat_medium', 'greenhouse_small'])
    gc.check_agent('atmosphere_equalizer', id=1, amount=1, in_conn=eq_conn, out_conn=eq_conn)

    # Power Storage
    gc.check_agent('power_storage', amount=2)

    # Plants
    greenhouse = 'greenhouse_small'
    plant_in = dict(atmo_co2=[greenhouse], h2o_potb=['water_storage'],
                    sold_n=['nutrient_storage'], sold_p=['nutrient_storage'],
                    sold_k=['nutrient_storage'], enrg_kwh=['power_storage'],
                    biomass_totl=['nutrient_storage'])
    plant_out = dict(atmo_o2=[greenhouse], atmo_h2o=[greenhouse],
                     food_edbl=['food_storage'], biomass_totl=['nutrient_storage'])
    garden = dict(wheat=20, cabbage=30, strawberry=10, radish=50, red_beet=50, onion=50)
    for plant, amount in garden.items():
        gc.check_agent(plant, amount=amount, in_conn=plant_in, out_conn=plant_out)
