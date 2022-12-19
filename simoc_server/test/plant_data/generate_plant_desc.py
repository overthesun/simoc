"""
This script updates the plant agents in agent_desc.json and agent_conn.json
based on the values in 'simoc-plant-exchanges.csv', and updates the config
files to be successful with new model.
"""

import json
import pathlib

import pandas as pd

ROUNDING_PRECISION = 6

def build_plant_desc(exchanges_path, data_files_path):

    # Load agent_desc file
    with open(data_files_path / 'agent_desc.json') as f:
        agent_desc = json.load(f)

    # Load plant exchanges, iterate through plants (rows)
    plant_exchanges = pd.read_csv(exchanges_path)
    for i, row in plant_exchanges.iterrows():
        plant_name = '_'.join(row['plant'].split(' '))
        def val(field):
            v = row[field]
            if isinstance(v, (int, float)):
                v = round(v, ROUNDING_PRECISION)
            return v

        # Convert to agent_desc schema
        plant_desc = {'data': {
            'input': [
                {
                    'type': 'co2',
                    'value': val('in_co2'),
                    'required': 'desired',
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'deprive': {'value': 72, 'unit': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'cu_factor']
                }, {
                    'type': 'potable',
                    'value': val('in_potable'),
                    'required': 'desired',
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'deprive': {'value': 72, 'unit': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'te_factor']
                }, {
                    'type': 'fertilizer',
                    'value': val('in_fertilizer'),
                    'required': 'desired',
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'deprive': {'value': 72, 'unit': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'cu_factor']
                }, {
                    'type': 'par',  # Dummy exchange to force connection setup
                    'value': 0,
                    'flow_rate': {'unit': 'mol', 'time': 'hour'},
                }
            ],
            'output': [
                {
                    'type': 'o2',
                    'value': val('out_o2'),
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'requires': ['co2'],
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'cu_factor']
                }, {
                    'type': 'h2o',
                    'value': val('out_h2o'),
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'requires': ['potable'],
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'te_factor']
                }, {
                    'type': 'biomass',
                    'value': val('out_biomass'),
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    "growth": {"lifetime": {"type": "norm"}},
                    'weighted': ['daily_growth_factor', 'par_factor', 'cu_factor']
                }, {
                    # HARVEST
                    'type': plant_name,  # Food
                    'value': val('char_harvest_index'),
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'weighted': ['biomass'],
                    'criteria': {'name': 'grown', 'limit': '=', 'value': True},
                }, {
                    'type': 'inedible_biomass',
                    'value': 1 - val('char_harvest_index'),
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'weighted': ['biomass'],
                    'criteria': {'name': 'grown', 'limit': '=', 'value': True},
                }
            ],
            'characteristics': [
                {'type': 'par_baseline', 'value': val('char_par_baseline'), 'unit': 'mol'},
                {'type': 'photoperiod', 'value': val(f'char_photoperiod'), 'unit': 'hour'},
                {'type': 'lifetime', 'value': val(f'char_lifetime')*24, 'unit': 'hour'},
                {'type': 'carbon_fixation', 'value': val('char_carbon_fixation')},
                {'type': 'harvest_index', 'value': val('char_harvest_index')},
                {'type': 'reproduce', 'value': True},
                {'type': 'capacity_biomass',
                 'value': round(val('out_biomass') * val('char_lifetime') * 24,
                                ROUNDING_PRECISION),
                 'unit': 'kg'},
            ]
        }}

        # Replace or add to agent_desc
        old_record = agent_desc['plants'].get(plant_name, None)
        if old_record is not None:
            plant_desc['description'] = old_record.get('description', '')
        agent_desc['plants'][plant_name] = plant_desc

    # Make sure all are included in food_storage
    if 'storage' in agent_desc and 'food_storage' in agent_desc['storage']:
        fs = agent_desc['storage']['food_storage']['data']['characteristics']
        chars = [c for c in fs if not c['type'].startswith('capacity')]
        for plant in agent_desc['plants']:
            char = {"type": f"capacity_{plant}", "value": 10000, "unit": "kg"}
            chars.append(char)
        agent_desc['storage']['food_storage']['data']['characteristics'] = chars

    # Add a lamp
    # These factors are taken from the equation in column R of the
    # plant_nutrient_use-WHEELER spreadsheet and represent the conversion from
    # electric lamp to usable PAR.
    lamp_power_factor_1 = 1.66e-6
    lamp_power_factor_2 = 3.6e6
    agent_desc['structures']['lamp'] = {
        'data': {
            'input': [
                {
                    'type': 'kwh',
                    'value': (1/lamp_power_factor_1)/lamp_power_factor_2,  # 0.19522...
                    'required': 'desired',
                    'flow_rate': {'unit': 'kWh', 'time': 'hour'},
                    'weighted': ['par_baseline', 'daily_growth_factor'],
                }
            ],
            'output': [
                {
                    'type': 'par',
                    'value': 1,
                    'requires': ['kwh'],
                    'flow_rate': {'unit': 'mol', 'time': 'hour'},
                    'weighted': ['par_baseline', 'daily_growth_factor'],
                }
            ],
            'characteristics': [
                {
                    'type': 'par_baseline',
                    'value': 5,
                    'unit': 'mol/m2-hr',
                }, {
                    'type': 'capacity_par',
                    'value': 10_000,
                    'unit': 'mol',
                }, {
                    'type': 'custom_function',
                    'value': 'electric_lamp',
                }
            ],
        }
    }

    # Update CO2 regulation system to higher baseline
    for agent, value in {('co2_removal_SAWD', .001),
                         ('co2_makeup_valve', .0007)}:
        inputs = agent_desc['eclss'][agent]['data']['input']
        for i, input in enumerate(inputs):
            if input['type'] == 'co2':
                inputs[i]['criteria']['value'] = value
        agent_desc['eclss'][agent]['data']['input'] = inputs

    # Save updated agent_desc
    with open(data_files_path / 'agent_desc.json', 'w') as f:
        json.dump(agent_desc, f, indent=2)

    # Connections -------------------------------------------------------------
    try:
        with open(data_files_path / 'agent_conn.json') as f:
            agent_conn = json.load(f)
    except:
        agent_conn = []

    # Remove existing connections for plants
    all_plants = [p for p in agent_desc['plants']]
    all_plants.sort()
    def is_plant_connection(conn):
         _from, _to = conn['from'].split('.')[0], conn['to'].split('.')[0]
         return _from in all_plants or _to in all_plants
    agent_conn = [c for c in agent_conn if not is_plant_connection(c)]

    # Add new connections for each plant
    for plant in all_plants:
        agent_conn += [
            {'from': 'greenhouse.co2', 'to': f'{plant}.co2'},
            {'from': 'water_storage.potable', 'to': f'{plant}.potable'},
            {'from': 'nutrient_storage.fertilizer', 'to': f'{plant}.fertilizer'},
            {'from': 'lamp.par', 'to': f'{plant}.par'},
            {'from': f'{plant}.biomass', 'to': f'{plant}.biomass'},
            {'from': f'{plant}.inedible_biomass', 'to': 'nutrient_storage.inedible_biomass'},
            {'from': f'{plant}.o2', 'to': 'greenhouse.o2'},
            {'from': f'{plant}.h2o', 'to': 'greenhouse.h2o'},
            {'from': f'{plant}.{plant}', 'to': f'food_storage.{plant}'},
        ]

    # Add power connection to lamp
    def is_lamp_connection(conn):
        _to = conn['to'].split('.')[0]
        return _to == 'lamp'
    agent_conn = [c for c in agent_conn if not is_lamp_connection(c)]
    agent_conn += [
        {'from': 'power_storage.kwh', 'to': 'lamp.kwh'},
        {'from': 'lamp.par', 'to': 'lamp.par'},
    ]

    # Change dehumidifier connection from crew habitat to greenhouse
    agent_conn = [c for c in agent_conn if c['to'] != 'dehumidifier.h2o']
    agent_conn += [
        {'from': 'greenhouse.h2o', 'to': 'dehumidifier.h2o', 'priority': 0},
        {'from': 'habitat.h2o', 'to': 'dehumidifier.h2o', 'priority': 1},
    ]

    # Save updated agent_conn
    with open(data_files_path / 'agent_conn.json', 'w') as f:
        json.dump(agent_conn, f)

    # Currencies -------------------------------------------------------------
    try:
        with open(data_files_path / 'currency_desc.json') as f:
            currency_desc = json.load(f)
    except:
        currency_desc = {'food': {}}

    # Add plants which wheren't included
    for plant in all_plants:
        if plant not in currency_desc['food']:
            label = ' '.join([word.capitalize() for word in plant.split('_')])
            currency_desc['food'][plant] = {'label': label, 'unit': 'kg'}
    # Add par
    currency_desc['energy']['par'] = {
        'label': 'Photosynthetically Active Radiation', 'unit': 'moles/m2-h'}

    with open(data_files_path / 'currency_desc.json', 'w') as f:
        json.dump(currency_desc, f)


    # Preset Configurations ---------------------------------------------------

    # 1 human + radish
    fname = data_files_path / 'config_1hg_sam.json'
    with open(fname) as f:
        config = json.load(f)
    # Increase ECLSS to handle updated plant growth
    config['agents']['lamp'] = dict(amount=1)
    config['agents']['co2_makeup_valve']['amount'] = 1
    config['agents']['dehumidifier']['amount'] = 3
    config['agents']['multifiltration_purifier_post_treatment']['amount'] = 1
    with open(fname, 'w') as f:
        json.dump(config, f)

    # 1 human + garden SAM
    fname = data_files_path / 'config_1hrad.json'
    with open(fname) as f:
        config = json.load(f)
    config['agents']['lamp'] = dict(amount=1)
    config['agents']['co2_removal_SAWD']['amount'] = 1
    config['agents']['co2_makeup_valve']['amount'] = 1
    config['agents']['dehumidifier']['amount'] = 3
    config['agents']['multifiltration_purifier_post_treatment']['amount'] = 1
    config['agents']['solar_pv_array_mars']['amount'] = 100
    with open(fname, 'w') as f:
        json.dump(config, f)

    # 4 humans + garden
    fname = data_files_path / 'config_4hg.json'
    with open(fname) as f:
        config = json.load(f)
    config['agents']['lamp'] = dict(amount=1)
    config['agents']['co2_removal_SAWD']['amount'] = 2
    config['agents']['co2_makeup_valve']['amount'] = 4
    config['agents']['dehumidifier']['amount'] = 5
    config['agents']['multifiltration_purifier_post_treatment']['amount'] = 3
    config['agents']['solar_pv_array_mars']['amount'] = 500
    with open(fname, 'w') as f:
        json.dump(config, f)


if __name__ == '__main__':

    # A .csv file with rows matching currency exchanges / characteristics
    exchanges_path = pathlib.Path('simoc_server/test/plant_data/simoc-plant-exchanges.csv')
    # A .json file (new or existing) following the SIMOC json schemas
    data_files_path = pathlib.Path('data_files')

    build_plant_desc(exchanges_path, data_files_path)
