import json

import pytest
from pytest import approx

from simoc_server.front_end_routes import convert_configuration
from agent_model.parse_data_files import parse_currency_desc, parse_agent_desc, \
                                         parse_agent_conn, merge_json

def test_parse_currency_desc(currency_desc):
    currencies, currency_errors = parse_currency_desc(currency_desc)

    assert len(currencies) == 43
    # with open('data_analysis/parsed_currency_desc.json', 'w') as f:
    #     json.dump(currencies, f)

    atm = currencies['atmosphere']
    assert atm['name'] == 'atmosphere'
    assert atm['id'] > 100
    assert atm['type'] == 'currency_class'
    for c in ['o2', 'co2', 'h2', 'n2', 'h2o', 'ch4']:
        assert c in atm['currencies']

    o2 = currencies['o2']
    assert o2['name'] == 'o2'
    assert o2['id'] > 100
    assert o2['type'] == 'currency'
    assert o2['class'] == 'atmosphere'
    assert o2['label'] == 'Oxygen'

def test_parse_agent_desc(four_humans_garden, currency_dict, agent_desc):
    config = convert_configuration(four_humans_garden)
    agents, agent_errors = parse_agent_desc(config, currency_dict, agent_desc, 'mars')
    # with open('data_analysis/parsed_agent_desc.json', 'w') as f:
    #     json.dump(agents, f)

    assert len(agents) == 26

    assert agents['strawberry']['agent_class'] == 'plants'

    def _attr(attr_name):
        attribute = agents['strawberry']['attributes'][attr_name]
        attribute_detail = agents['strawberry']['attribute_details'][attr_name]
        return attribute, attribute_detail

    category, _ = _attr('char_category')
    assert category == 'food_frut'

    lifetime, lifetime_detail = _attr('char_lifetime')
    assert lifetime == 2040
    assert lifetime_detail['unit'] == 'hour'

    growth_criteria, _ = _attr('char_growth_criteria')
    assert growth_criteria == 'out_biomass'

    reproduce, _ = _attr('char_reproduce')
    assert reproduce == True

    co2, co2_details = _attr('in_co2')
    assert co2 == 0.0007907178481
    assert co2_details['flow_unit'] == 'kg'
    assert co2_details['flow_time'] == 'hour'
    assert co2_details['deprive_unit'] == 'hour'
    assert co2_details['deprive_value'] == 72
    assert co2_details['is_required'] == 'desired'
    assert co2_details['is_growing'] == 1
    assert co2_details['lifetime_growth_type'] == 'sigmoid'
    assert co2_details['daily_growth_type'] == 'norm'

    potable, _ = _attr('in_potable')
    assert potable == 0.0054183333333

    fertilizer, _ = _attr('in_fertilizer')
    assert fertilizer == 2.09e-05

    kwh, kwh_details = _attr('in_kwh')
    assert kwh == 0.1533913432
    assert kwh_details['daily_growth_type'] == 'switch'
    assert kwh_details['daily_growth_min_threshold'] == 0.25
    assert kwh_details['daily_growth_max_threshold'] == 0.75

    in_biomass, in_biomass_details = _attr('in_biomass')
    assert in_biomass == 1
    assert in_biomass_details['weighted'] == 'current_growth'
    assert in_biomass_details['criteria_name'] == 'grown'
    assert in_biomass_details['criteria_limit'] == '='
    assert in_biomass_details['criteria_value'] == True

    o2, _ = _attr('out_o2')
    assert o2 == 0.0005763666242

    h2o, _ = _attr('out_h2o')
    assert h2o == 0.0047265009912

    strawberry, _ = _attr('out_strawberry')
    assert strawberry == 0.35011

    out_biomass, out_biomass_details = _attr('out_biomass')
    assert out_biomass == 0.000927083
    assert out_biomass_details['lifetime_growth_type'] == 'norm'
    assert out_biomass_details['lifetime_growth_max_value'] == 0.00369864

def test_merge_json(agent_desc, currency_desc):
    user_agent_desc = {
        'eclss': {
            'co2_removal_SAWD': {
                'data': {
                    'input': [
                        {
                            'type': 'co2',
                            'criteria': {
                                'value': 0.001,
                                'buffer': 2
                            }
                        }
                    ]
                }
            },
            'co2_makeup_valve': {
                'data': {
                    'input': [
                        {
                            'type': 'co2',
                            'criteria': {
                                'value': 0.001,
                                'buffer': 2
                            }
                        }
                    ]
                }
            }
        }
    }
    merged = merge_json(agent_desc, user_agent_desc)
    assert len(merged.keys()) == 10
    assert len(merged['eclss'].keys()) == 10
    assert merged['eclss']['co2_makeup_valve']['data']['input'][0]['criteria']['value'] == 0.001
    assert merged['eclss']['co2_makeup_valve']['data']['input'][0]['criteria']['buffer'] == 2
    assert merged['eclss']['co2_removal_SAWD']['data']['input'][0]['criteria']['value'] == 0.001
    assert merged['eclss']['co2_removal_SAWD']['data']['input'][0]['criteria']['buffer'] == 2

    user_currency_desc = {
        "food": {
            "mushroom": {
                "label": "Mushroom"
            },
            "rice": {
                "label": "Not rice"
            }
        }
    }
    merged = merge_json(currency_desc, user_currency_desc)
    food = merged['food']
    assert len(food) == 24
    assert food['mushroom']['label'] == 'Mushroom'
    assert food['rice']['label'] == 'Not rice'

def test_parse_agent_conn(four_humans_garden, agent_desc, currency_dict, agent_conn):
    config = convert_configuration(four_humans_garden)
    active_agents = list(config['agents'].keys())
    connections, conn_errors = parse_agent_conn(active_agents, agent_conn)

    for agent in connections.values():
        for direction in ['in', 'out']:
            for currency, connected_agents in agent[direction].items():
                assert currency in currency_dict
                for conn in connected_agents:
                    assert conn in connections
