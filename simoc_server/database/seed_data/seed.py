from . import seed_agents, seed_model, seed_alerts

def seed():
    seed_agents.seed()
    seed_model.seed()
    seed_alerts.seed()