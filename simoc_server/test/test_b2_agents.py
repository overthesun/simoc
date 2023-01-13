import time
import json
import copy
import random
import datetime

import pytest

from simoc_server.front_end_routes import convert_configuration
from agent_model import AgentModel
from agent_model.util import parse_data

def test_b2_sun():

    # Convert the 1 human + radish config
    with open('data_files/config_1hrad.json') as f:
        config = json.load(f)
    config['agents']['b2_sun'] = {'amount': 1}
    config['start_time'] = '1993-03-11 00:00:00'
    config['location'] = 'earth'
    agent_conn = [{'from': 'b2_sun.par', 'to': f'radish.par'}]

    # Check that sun corrects for date range
    def get_t1_sun_output(start_time):
        _config = copy.deepcopy(config)
        _config['start_time'] = start_time
        _model = AgentModel.from_config(_config, agent_conn)
        _model.step()
        _sun_agent = _model.get_agents_by_type('b2_sun')[0]
        return _sun_agent.par
    in_range = get_t1_sun_output('1991-03-01 00:00:00')
    out_range = get_t1_sun_output('1990-03-01 00:00:00')
    assert in_range == out_range

    # Run the model
    model = AgentModel.from_config(config, agent_conn=agent_conn)
    model.step_to(n_steps=6)
    data = model.get_data()

    # Check the output of the sun
    sun_par = parse_data(data, ['b2_sun', 'storage', 'par'])
    assert sun_par == [0.060463168314734195, 0.058569909024987606, 0.058569909024987606,
                       0.4276509101374024, 0.47740164191306284, 0.473930668020504]
    # Check that plant is responding correctly
    plant_par = parse_data(data, ['radish', 'growth', 'par_factor'])
    assert plant_par == [0, 0, 0, 0, 0.44203855732691, 0.43882469261157775]


