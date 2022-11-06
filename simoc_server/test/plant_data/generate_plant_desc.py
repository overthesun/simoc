import json
import pandas as pd

"""
This script updates the plant agents in agent_desc.json and agent_conn.json
based on the values in 'simoc-plant-exchanges.csv'
"""

def build_plant_desc(exchanges_path, agent_desc_path, agent_conn_path,
                     currency_desc_path):

    # Load agent_desc file or create new
    try:
        with open(agent_desc_path) as f:
            agent_desc = json.load(f)
    except:
        print('Source agent_desc not found, generating new')
        agent_desc = {'plants': {}}

    # Load plant exchanges, iterate through plants (rows)
    plant_exchanges = pd.read_csv(exchanges_path)
    for i, row in plant_exchanges.iterrows():
        plant_name = '_'.join(row['plant'].split(' '))

        # Convert to agent_desc schema
        plant_desc = {'data': {
            'input': [
                {
                    'type': 'par',  # Dummy exchange to force connection setup
                    'value': 0,
                    'flow_rate': {'unit': 'mol', 'time': 'hour'},
                }, {
                    'type': 'co2',
                    'value': row['in_co2'],
                    'required': 'desired',
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'deprive': {'value': 72, 'unit': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'cu_factor']
                }, {
                    'type': 'potable',
                    'value': row['in_potable'],
                    'required': 'desired',
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'deprive': {'value': 72, 'unit': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'te_factor']
                }, {
                    'type': 'fertilizer',
                    'value': row['in_fertilizer'],
                    'required': 'desired',
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'deprive': {'value': 72, 'unit': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'cu_factor']
                },
            ],
            'output': [
                {
                    'type': 'o2',
                    'value': row['out_o2'],
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'cu_factor']
                }, {
                    'type': 'h2o',
                    'value': row['out_h2o'],
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'te_factor']
                }, {
                    'type': 'biomass',
                    'value': row['out_biomass'],
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    "growth": {"lifetime": {"type": "norm"}},
                    'weighted': ['daily_growth_factor', 'par_factor', 'cu_factor']
                }, {
                    # HARVEST
                    'type': plant_name,  # Food
                    'value': row['char_harvest_index'],
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'weighted': ['growth_rate'],
                    'criteria': {'name': 'grown', 'limit': '=', 'value': True},
                }, {
                    'type': 'inedible_biomass',
                    'value': 1 - row['char_harvest_index'],
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'weighted': ['growth_rate'],
                    'criteria': {'name': 'grown', 'limit': '=', 'value': True},
                }
            ],
            'characteristics': [
                {'type': 'par_baseline', 'value': row['char_par_baseline'], 'unit': 'mol'},
                {'type': 'photoperiod', 'value': row[f'char_photoperiod'], 'unit': 'hour'},
                {'type': 'lifetime', 'value': row[f'char_lifetime']*24, 'unit': 'hour'},
                {'type': 'carbon_fixation', 'value': row['char_carbon_fixation']},
                {'type': 'harvest_index', 'value': row['char_harvest_index']},
                {'type': 'reproduce', 'value': True},
                {'type': 'capacity_biomass',
                 'value': round(row['out_biomass'] * row['char_lifetime'] * 24, 6),
                 'unit': 'kg'},
            ]
        }}

        # Add to agent_desc
        old_record = agent_desc['plants'].get(plant_name, None)
        if old_record is not None:
            plant_desc['description'] = old_record.get('description', '')
            del agent_desc['plants'][plant_name]
        agent_desc['plants'][plant_name] = plant_desc

    # Make sure all are included in food_storage
    if 'storage' in agent_desc and 'food_storage' in agent_desc['storage']:
        fs = agent_desc['storage']['food_storage']['data']['characteristics']
        chars = [c for c in fs if not c['type'].startswith('capacity')]
        for plant in agent_desc['plants']:
            char = {"type": f"capacity_{plant}", "value": 10000, "unit": "kg"}
            chars.append(char)
        agent_desc['storage']['food_storage']['data']['characteristics'] = chars

    # Add a light
    agent_desc['structures']['light'] = {
        'data': {
            'input': [],
            'output': [],
            'characteristics': [
                {
                    'type': 'capacity_par',
                    'value': 1000,
                    'unit': 'mol',
                }, {
                    'type': 'custom_function',
                    'value': 'electric_light',
                }
            ],
        }
    }

    # Save updated agent_desc
    with open(agent_desc_path, 'w') as f:
        json.dump(agent_desc, f)

    # Connections -------------------------------------------------------------
    try:
        with open(agent_conn_path) as f:
            agent_conn = json.load(f)
    except:
        agent_conn = []

    # Remove existing connections for plants
    all_plants = {p for p in agent_desc['plants']}
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
            {'from': 'light.par', 'to': f'{plant}.par'},
            {'from': f'{plant}.biomass', 'to': f'{plant}.biomass'},
            {'from': f'{plant}.inedible_biomass', 'to': 'nutrient_storage.inedible_biomass'},
            {'from': f'{plant}.o2', 'to': 'greenhouse.o2'},
            {'from': f'{plant}.h2o', 'to': 'greenhouse.h2o'},
            {'from': f'{plant}.{plant}', 'to': f'food_storage.{plant}'},
        ]

    # Save updated agent_conn
    with open(agent_conn_path, 'w') as f:
        json.dump(agent_conn, f)

    # Currencies -------------------------------------------------------------
    try:
        with open(currency_desc_path) as f:
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

    with open(currency_desc_path, 'w') as f:
        json.dump(currency_desc, f)

if __name__ == '__main__':
    """TODO: Add ArgParser to select source and desination explicitly"""

    # A .csv file with rows matching currency exchanges / characteristics
    exchanges_path = 'simoc_server/test/plant_data/simoc-plant-exchanges.csv'
    # A .json file (new or existing) following the SIMOC json schemas
    agent_desc_path = 'data_files/agent_desc.json'
    agent_conn_path = 'data_files/agent_conn.json'
    currency_desc_path = 'data_files/currency_desc.json'

    build_plant_desc(exchanges_path, agent_desc_path, agent_conn_path, currency_desc_path)
