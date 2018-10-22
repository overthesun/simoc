from . import seed_agents, seed_model, seed_alerts

def seed(agent_config):
    seed_agents.seed(agent_config)
    seed_model.seed()
    seed_alerts.seed()