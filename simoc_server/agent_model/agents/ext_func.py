from simoc_server import db
from simoc_server.database.db_model import AgentType, AgentState, CurrencyType

def atmosphere_equalizer(agent):
    habitat = [a for a in agent.selected_storage['in']['atmo'] if 'habitat' in a.agent_type][0]
    greenhouse = [a for a in agent.selected_storage['in']['atmo'] if 'greenhouse' in a.agent_type][0]
    if not habitat or not greenhouse:
        return
    habitat_volume = habitat.attrs['char_volume']
    greenhouse_volume = greenhouse.attrs['char_volume']
    net_volume = habitat_volume + greenhouse_volume
    habitat_gasses = habitat.views(view='atmo')
    greenhouse_gasses = greenhouse.views(view='atmo')
    combined_gasses = [c for c in {**habitat_gasses, **greenhouse_gasses}]
    max_flow = 50
    deltas = {}
    for gas in combined_gasses:
        net_mass = getattr(habitat, gas, 0) + getattr(greenhouse, gas, 0)
        equalized = net_mass / net_volume
        deltas[gas] = habitat[gas] - (equalized * habitat_volume)
    net_flow = sum([abs(v) for k, v in deltas.items()])
    flow_rate = min(1, max_flow/net_flow) if net_flow else 1
    for gas, amount in deltas.items():
        amount_adj = amount * flow_rate
        habitat[gas] -= amount_adj
        greenhouse[gas] += amount_adj
