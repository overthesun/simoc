import pytest

from simoc_server import front_end_routes

eclss_agents = ['solid_waste_aerobic_bioreactor', 'multifiltration_purifier_post_treatment',
                'oxygen_generation_SFWE', 'urine_recycling_processor_VCD', 'co2_removal_SAWD',
                'co2_makeup_valve', 'co2_storage', 'co2_reduction_sabatier',
                'ch4_removal_agent', 'dehumidifier']


class GameConfig:
    def __init__(self, game_config):
        self.game_config = front_end_routes.convert_configuration(game_config)

    def termination(self):
        return self.game_config.get('termination', None)

    def single_agent(self):
        return self.game_config.get('single_agent', None)

    def priorities(self):
        return self.game_config.get('priorities', None)

    def total_amount(self):
        return self.game_config.get('total_amount', None)

    def agents(self):
        return self.game_config.get('agents', None)

    def check_agent(self, agent_type, id=None, amount=None, currencies=None,
                    in_conn=None, out_conn=None):
        agents = self.agents()
        assert agent_type in agents
        agent = agents[agent_type]
        if id:
            assert agent['id'] == id
        if amount:
            assert agent['amount'] == amount
        if currencies:
            for curr in currencies:
                assert curr in agent
            if isinstance(currencies, dict):
                for curr, bal in currencies.items():
                    assert agent[curr] == bal
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


# Test basic fields
def test_convert_one_human(one_human):
    gc = GameConfig(one_human)

    # Game Variables
    assert gc.single_agent() == 1
    assert gc.total_amount() == 17

    termination = gc.termination()
    assert termination[0]['condition'] == 'time'
    assert termination[0]['value'] == 10
    assert termination[0]['unit'] == 'day'

    priorities = gc.priorities()
    expected_priorities = ['structures', 'storage', 'power_generation',
                           'inhabitants', 'eclss', 'plants']
    for i, agent_class in enumerate(expected_priorities):
        assert priorities[i] == agent_class

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
    atmo_currencies = ['atmo_n2', 'atmo_o2', 'atmo_co2', 'atmo_ch4', 'atmo_h2', 'atmo_h2o']
    gc.check_agent('crew_habitat_small', id=1, amount=1, currencies=atmo_currencies)
    assert 'atmosphere_equalizer' not in gc.agents()

    # Storages
    water_curr = ['h2o_potb', 'h2o_tret', 'h2o_urin', 'h2o_wste']
    gc.check_agent('water_storage', id=1, amount=1, currencies=water_curr)
    nutrient_curr = ['sold_n', 'sold_p', 'sold_k', 'biomass_totl', 'biomass_edible', 'sold_wste']
    gc.check_agent('nutrient_storage', id=1, amount=1, currencies=nutrient_curr)
    gc.check_agent('food_storage', id=1, amount=1, currencies=['food_edbl'])
    gc.check_agent('power_storage', id=1, amount=1, currencies=['enrg_kwh'])

    # ECLSS
    for agent in eclss_agents:
        gc.check_agent(agent, id=1, amount=1)

# Test with greenhouse and plants
def test_convert_four_humans_garden(four_humans_garden):
    gc = GameConfig(four_humans_garden)

    # Structures
    habitat_currencies = {
        "atmo_n2": 2205.873,
        "atmo_o2": 591.7245,
        "atmo_co2": 1.167629,
        "atmo_ch4": 0.005282749999999999,
        "atmo_h2": 0.0015537500000000002,
        "atmo_h2o": 28.25,
    }
    gc.check_agent('crew_habitat_medium', id=1, amount=1, currencies=habitat_currencies)
    greenhouse_currencies = {
        "atmo_n2": 478.26450000000006,
        "atmo_o2": 128.29425,
        "atmo_co2": 0.2531585,
        "atmo_ch4": 0.001145375,
        "atmo_h2": 0.00033687500000000004,
        "atmo_h2o": 6.125,
    }
    gc.check_agent('greenhouse_small', id=1, amount=1, currencies=greenhouse_currencies)
    eq_conn = dict(atmo=['crew_habitat_medium', 'greenhouse_small'])
    gc.check_agent('atmosphere_equalizer', id=1, amount=1, in_conn=eq_conn, out_conn=eq_conn)

    # Power Storage
    gc.check_agent('power_storage', amount=2)

    # Plants
    greenhouse = 'greenhouse_small'
    plant_in=dict(atmo_co2=[greenhouse], h2o_potb=['water_storage'],
                  sold_n=['nutrient_storage'], sold_p=['nutrient_storage'],
                  sold_k=['nutrient_storage'], enrg_kwh=['power_storage'],
                  biomass_totl=['nutrient_storage'])
    plant_out=dict(atmo_o2=[greenhouse], atmo_h2o=[greenhouse],
                   food_edbl=['food_storage'], biomass_totl=['nutrient_storage'])
    garden = dict(wheat=20, cabbage=30, strawberry=10, radish=50, red_beet=50, onion=50)
    for plant, amount in garden.items():
        gc.check_agent(plant, amount=amount, in_conn=plant_in, out_conn=plant_out)
