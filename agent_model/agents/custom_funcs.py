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
