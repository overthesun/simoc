from . import seed_agents, seed_model

def seed(agent_config):
    seed_agents.seed(agent_config)
    seed_model.seed()
