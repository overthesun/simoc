from .human import HumanAgent
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from simoc_server.database.db_model import AgentModelEntity, AgentEntity, AgentType
from simoc_server import db

class AgentModel(object):

    def __init__(self, grid_width=None, grid_height=None, agent_model_entity=None):
        if agent_model_entity is not None:
            self.load_from_db(agent_entity)
        else:
            self.init_new(grid_width ,grid_height)
            agent_model_entity = self.create_entity()

        self.agent_model_entity = agent_model_entity

        human_agent_type = AgentType.query.filter_by(name="Human").first()
        human_agent_entity = AgentEntity.query.filter_by(agent_type=human_agent_type).first()
        if human_agent_entity:
            human_agent = HumanAgent(self, human_agent_entity)
            print("Loaded human agent from db with energy={0}".format(human_agent.energy))
            human_agent.energy -= 1
            print("Changing human agent to energy={0}".format(human_agent.energy))
        else:
            human_agent = HumanAgent(self)
            print("Created human agent with energy={0}".format(human_agent.energy))
        self.add_agent(human_agent, (0,0))
        print("Saving human agent to db with energy={0}".format(human_agent.energy))
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