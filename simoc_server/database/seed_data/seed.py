from . import seed_agents, seed_model

def seed():
    seed_agents.seed()
    seed_model.seed()