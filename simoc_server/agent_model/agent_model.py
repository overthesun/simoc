from .human import HumanAgent
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from simoc_server.database.db_model import AgentModelEntity
from simoc_server import db

class AgentModel(object):

    def __init__(self, grid_width=None, grid_height=None, agent_model_entity=None):
        if agent_model_entity is not None:
            self.load_from_db(agent_entity)
        else:
            self.init_new(grid_width ,grid_height)
            agent_model_entity = self.create_entity()

        self.agent_model_entity = agent_model_entity

        self.add_agent(HumanAgent(self), (0,0))
        self.save()

    def init_new(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = MultiGrid(self.grid_width, self.grid_height, True)
        self.scheduler = RandomActivation(self)

    def create_entity(self):
        agent_model_entity = AgentModelEntity()
        return agent_model_entity

    def add_agent(self, agent, pos):
        self.scheduler.add(agent)
        self.grid.place_agent(agent, pos)

    def num_agents(self):
        return len(self.schedule.agents)

    def save(self):
        db.session.add(self.agent_model_entity)
        for agent in self.scheduler.agents:
            agent.save(commit=False)
        db.session.commit()