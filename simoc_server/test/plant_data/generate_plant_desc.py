import json
import pandas as pd

"""
This script updates the plant agents in agent_desc.json and agent_conn.json
based on the values in 'simoc-plant-exchanges.csv'
"""

def build_plant_desc(exchanges_path, data_files_path):

    # Load agent_desc file or create new
    try:
        with open(data_files_path + '/agent_desc.json') as f:
            agent_desc = json.load(f)
    except:
        print('Source agent_desc not found, generating new')
        agent_desc = {'plants': {}}

    # Load plant exchanges, iterate through plants (rows)
    plant_exchanges = pd.read_csv(exchanges_path)
    for i, row in plant_exchanges.iterrows():
        plant_name = '_'.join(row['plant'].split(' '))
        def val(field):
            v = row[field]
            if isinstance(v, (int, float)):
                v = round(v, 6)
            return v

        # Convert to agent_desc schema
        plant_desc = {'data': {
            'input': [
                {
                    'type': 'par',  # Dummy exchange to force connection setup
                    'value': 0,
                    'flow_rate': {'unit': 'mol', 'time': 'hour'},
                }, {
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
                },
            ],
            'output': [
                {
                    'type': 'o2',
                    'value': val('out_o2'),
                    'requires': ['co2'],
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'cu_factor']
                }, {
                    'type': 'h2o',
                    'value': val('out_h2o'),
                    'requires': ['potable'],
                    'flow_rate': {'unit': 'kg', 'time': 'hour'},
                    'weighted': ['daily_growth_factor', 'par_factor', 'growth_rate', 'te_factor']
                }, {
                    'type': 'biomass',
                    'value': val('out_biomass'),
                    # 'requires': ['co2', 'potable', 'fertilizer'],  # Causes actual to be zero??
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
                 'value': round(val('out_biomass') * val('char_lifetime') * 24, 6),
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

    # Update CO2 regulation system to higher baseline
    for agent, value in {('co2_removal_SAWD', .0025),
                         ('co2_makeup_valve', .002)}:
        inputs = agent_desc['eclss'][agent]['data']['input']
        for i, input in enumerate(inputs):
            if input['type'] == 'co2':
                inputs[i]['criteria']['value'] = value
        agent_desc['eclss'][agent]['data']['input'] = inputs

    # Save updated agent_desc
    with open(data_files_path + '/agent_desc.json', 'w') as f:
        json.dump(agent_desc, f)

    # Connections -------------------------------------------------------------
    try:
        with open(data_files_path + '/agent_conn.json') as f:
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
            {'from': 'light.par', 'to': f'{plant}.par'},
            {'from': f'{plant}.biomass', 'to': f'{plant}.biomass'},
            {'from': f'{plant}.inedible_biomass', 'to': 'nutrient_storage.inedible_biomass'},
            {'from': f'{plant}.o2', 'to': 'greenhouse.o2'},
            {'from': f'{plant}.h2o', 'to': 'greenhouse.h2o'},
            {'from': f'{plant}.{plant}', 'to': f'food_storage.{plant}'},
        ]

    # Save updated agent_conn
    with open(data_files_path + '/agent_conn.json', 'w') as f:
        json.dump(agent_conn, f)

    # Currencies -------------------------------------------------------------
    try:
        with open(data_files_path + '/currency_desc.json') as f:
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

    with open(data_files_path + '/currency_desc.json', 'w') as f:
        json.dump(currency_desc, f)


    # Preset Configurations ---------------------------------------------------
    """
    1. Add light agent
    2. Increase co2_makeup_valve amount, co2_storage starting co2
    3. Update agent_desc for co2_removal_SAWD and valve to higher thresholds
    """
    update_config = {
        # '1h': dict(),
        '1hg_sam': dict(makeup_valves=3, starting_co2=200, dehumidifiers=3, purifiers=3),
        '1hrad': dict(makeup_valves=3, starting_co2=200, dehumidifiers=3, purifiers=3),
        # '4h': dict(),
        '4hg': dict(makeup_valves=3, starting_co2=200, dehumidifiers=3, purifiers=3),
        # 'disaster': dict(),
    }
    for config_name, changes in update_config.items():
        fpath = f'{data_files_path}/config_{config_name}.json'
        with open(fpath) as f:
            config = json.load(f)

        # Add a light agent
        config['agents']['light'] = {'amount': 1}

        # Increase the number of co2 makeup valves to keep up with
        config['agents']['co2_makeup_valve']['amount'] = changes['makeup_valves']
        config['agents']['co2_storage']['co2'] = changes['starting_co2']

        # Increase water management
        config['agents']['dehumidifier']['amount'] = changes['dehumidifiers']
        config['agents']['multifiltration_purifier_post_treatment']['amount'] = changes['purifiers']

        with open(fpath, 'w') as f:
            json.dump(config, f)

if __name__ == '__main__':
    """TODO: Add ArgParser to select source and desination explicitly"""

    # A .csv file with rows matching currency exchanges / characteristics
    exchanges_path = 'simoc_server/test/plant_data/simoc-plant-exchanges.csv'
    # A .json file (new or existing) following the SIMOC json schemas
    data_files_path = 'data_files'

    build_plant_desc(exchanges_path, data_files_path)
