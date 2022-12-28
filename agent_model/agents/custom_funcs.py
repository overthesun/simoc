def atmosphere_equalizer(agent):
    atmo_in_agents = agent.selected_storage['in']['atmosphere']
    habitat = next(a for a in atmo_in_agents if 'habitat' in a.agent_type)
    greenhouse = next(a for a in atmo_in_agents if 'greenhouse' in a.agent_type)
    if not habitat or not greenhouse:
        return
    habitat_volume = habitat.attrs['char_volume']
    greenhouse_volume = greenhouse.attrs['char_volume']
    net_volume = habitat_volume + greenhouse_volume
    habitat_gasses = habitat.view(view='atmosphere')
    greenhouse_gasses = greenhouse.view(view='atmosphere')
    combined_gasses = {**habitat_gasses, **greenhouse_gasses}.keys()
    max_flow = 50
    deltas = {}
    for gas in combined_gasses:
        net_mass = getattr(habitat, gas, 0) + getattr(greenhouse, gas, 0)
        equalized = net_mass / net_volume
        deltas[gas] = habitat[gas] - (equalized * habitat_volume)
    net_flow = sum(map(abs, deltas.values()))
    flow_rate = min(1, max_flow/net_flow) if net_flow else 1
    for gas, amount in deltas.items():
        amount_adj = amount * flow_rate
        habitat[gas] -= amount_adj
        greenhouse[gas] += amount_adj

def electric_lamp(agent):
    """Control the output of electric lamps

    Available light is represented by stored 'par' (photosynthetically active
    radiation). Lights 'step' before plants; each step old par is removed and
    new par is added.

    Two types of electric lamps are supported:
    - Generic lamp agent (included in agent_desc). Amount is adjusted to the
      number of plants, operate 24h/day.
    - Plant-specific agents (custom). Lamps can be assigned to an individual
      plant species by duplicating the generic light from the agent_desc and
      re-naming as e.g. 'potato_lamp'. In this case lamp operation matches
      the target plant's daily_growth_factor.
    """
    # Initialize
    if not hasattr(agent, 'daily_growth_factor'):
        # Weights used by exchanges; must be initialized
        agent.daily_growth_factor = 1
        agent.par_baseline = agent.attrs['char_par_baseline']

        # lamps may be assigned to specific plants by adding the name of the
        # plant in the agent_type, e.g. 'potato_lamp'. If this is done, the
        # code below will adjust lamp's operation based on the connected
        # plant's growth schedule and amount.
        named_agent = [a for a in agent.agent_type.split('_') if a != 'lamp']
        if len(named_agent) == 0:
            agent.target_plant = None
            plant_agents = agent.model.get_agents_by_class('plants')
            agent.amount = sum([a.amount for a in plant_agents])
        else:
            named_agent = '_'.join(named_agent)
            target_plant = agent.model.get_agents_by_type(named_agent)[0]
            if not target_plant.agent_class == 'plants':
                raise ValueError('lamps can only be assigned to plant agents')
            agent.target_plant = target_plant

    # Remove all (leftover) par from storage every step
    agent['par'] = 0

    # If assigned to plant, update amount and daily_growth_factor every step
    if agent.target_plant is not None:
        # Update amount
        agent.amount = agent.target_plant.amount

        # Update daily_growth_factor
        hour_of_day = agent.model.step_num % int(agent.model.day_length_hours)
        agent.daily_growth_factor = agent.target_plant.daily_growth[hour_of_day]

import datetime

hourly_par_fraction = [  # Marino fig. 2a, mean par per hour/day, scaled to mean=1
    0.27330022, 0.06846029, 0.06631662, 0.06631662, 0.48421388, 0.54054486,
    0.5366148, 0.53923484, 0.57853553, 0.96171719, 1.40227785, 1.43849271,
    2.82234256, 3.00993782, 2.82915468, 2.43876788, 1.71301526, 1.01608314,
    0.56958994, 0.54054486, 0.54054486, 0.54316491, 0.54316491, 0.47766377,
]
monthly_par = [  # Maringo fig. 2c & 4, mean hourly par, monthly from Jan91 - Dec95
    0.54950686, 0.63372954, 0.7206446 , 0.92002863, 0.97663421, 0.95983702,
    0.89926235, 0.8211712 , 0.75722611, 0.68654778, 0.57748131, 0.49670542,
    0.53580063, 0.61396126, 0.69077189, 0.86995316, 0.82823278, 0.92457803,
    0.87140854, 0.83036469, 0.79133973, 0.67958089, 0.60519844, 0.49848609,
    0.49649926, 0.57264328, 0.74441785, 0.88318598, 0.93440528, 0.98428221,
    0.91292888, 0.80386089, 0.82544877, 0.67260636, 0.5776829 , 0.5265369,
    0.57708425, 0.6437935 , 0.74417503, 0.87688951, 0.92676186, 0.96316316,
    0.91269064, 0.86154311, 0.75853793, 0.69055809, 0.57138185, 0.51013218,
    0.53643822, 0.63480008, 0.7601048 , 0.87867323, 0.95278919, 1.00872435,
    0.92659387, 0.84716341, 0.81756864, 0.73746165, 0.59808571, 0.55165404,
]

def b2_sun(agent):
    """Controls the output of the sun at B2"""

    # Production Data
    time = agent.model.start_time + agent.model.time
    if time.year not in [1991, 1992, 1993, 1994, 1995]:
        # If outside data range, use 1991 data
        time = datetime.DateTime(1991, time.Month, time.Day, time.Hour, time.Minute, time.Second)
    i_month = time.month + 12 * (time.year - 1991)
    i_hour = time.hour
    agent.par = hourly_par_fraction[i_hour] * monthly_par[i_month]
