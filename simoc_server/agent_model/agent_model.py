import time
import numbers
import threading
import datetime
from .agent_name_mapping import agent_name_mapping
from . import HumanAgent, PlantAgent
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from simoc_server.database.db_model import AgentModelState, AgentState, \
    AgentType, AgentModelSnapshot, SnapshotBranch, AgentModelParam
from simoc_server import db
from uuid import uuid4
from sqlalchemy.orm.exc import StaleDataError

class AgentModel(object):

    def __init__(self, grid_width, grid_height, starting_step_num=0, snapshot_branch=None):
        self.load_params()
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = MultiGrid(self.grid_width, self.grid_height, True)
        self.scheduler = RandomActivation(self)
        self.step_num = starting_step_num
        self.scheduler.steps = starting_step_num
        self.snapshot_branch = snapshot_branch

    def load_params(self):
        params = AgentModelParam.query.all()
        for param in params:
            value_type_str = param.value_type
            if value_type_str != type(None).__name__:
                value_type = eval(value_type_str)
                self.__dict__[param.name] = value_type(param.value)
            else:
                self.__dict__[param.name] = None

    @classmethod
    def load_from_db(self, agent_model_state):
        snapshot_branch = agent_model_state.agent_model_snapshot.snapshot_branch
        grid_width = agent_model_state.grid_width
        grid_height = agent_model_state.grid_height
        step_num = agent_model_state.step_num
        model = AgentModel(grid_width, grid_height, starting_step_num=step_num, \
            snapshot_branch = snapshot_branch)

        for agent_state in agent_model_state.agent_states:
            agent_type_name = agent_state.agent_type.name
            agent_class = agent_name_mapping[agent_type_name]
            agent = agent_class(model, agent_state)
            model.add_agent(agent, agent.pos)
            print("Loaded {0} agent from db {1}".format(agent_type_name, agent.status_str()))
        return model

    @classmethod
    def create_new(self, grid_width, grid_height):
        model = AgentModel(grid_width, grid_height)
        # for testing
        human_agent = HumanAgent(model)
        model.add_agent(human_agent, (0,0))
        human_agent = HumanAgent(model)
        model.add_agent(human_agent, (1,2))
        plant_agent = PlantAgent(model)
        model.add_agent(plant_agent, (12, 1))
        plant_agent = PlantAgent(model)
        model.add_agent(plant_agent, (4, 4))
        return model

    def add_agent(self, agent, pos):
        self.scheduler.add(agent)
        self.grid.place_agent(agent, pos)

    def num_agents(self):
        return len(self.schedule.agents)


    def _branch(self):
        self.snapshot_branch = SnapshotBranch(parent_branch_id=self.snapshot_branch.id)

    def snapshot(self, commit=True):
        if self.snapshot_branch is None:
            self.snapshot_branch = SnapshotBranch()
        else:
            if(self.snapshot_branch.version_id is not None):
                self.snapshot_branch.version_id += 1
        try:
            last_saved_branch_state = AgentModelState.query \
                                .join(AgentModelSnapshot) \
                                .join(SnapshotBranch, SnapshotBranch.id == self.snapshot_branch.id) \
                                .order_by(AgentModelState.step_num.desc()) \
                                .limit(1) \
                                .first()
            if(last_saved_branch_state is not None and \
               last_saved_branch_state.step_num >= self.step_num):
                self._branch()
            agent_model_state = AgentModelState(step_num=self.step_num, grid_width=self.grid.width, grid_height=self.grid.height)
            snapshot = AgentModelSnapshot(agent_model_state=agent_model_state, snapshot_branch=self.snapshot_branch)
            db.session.add(agent_model_state)
            db.session.add(snapshot)
            db.session.add(self.snapshot_branch)
            for agent in self.scheduler.agents:
                agent.snapshot(agent_model_state, commit=False)
            if commit:
                db.session.commit()

            return snapshot
        except StaleDataError:
            print("WARNING: StaleDataError during snapshot, probably a simultaneous save, changing branch.")
            db.session.rollback()
            self._branch()
            return self.snapshot()

    def step(self):
        self.step_num += 1
        self.scheduler.step()
        print("{0} step_num {1}".format(self, self.step_num))

    def get_timedelta_since_start(self):
        return datetime.timedelta(minutes=self.minutes_per_step * self.step_num)

    def timedelta_per_step(self):
        return datetime.timedelta(minutes=self.minutes_per_step)

    def get_meters_per_grid_unit(self):
        return self.meters_per_grid_unit

    def grid_units_to_meters(self, dist_grid):
        if isinstance(dist_grid, tuple):
            return tuple(d * self.meters_per_grid_unit for d in dist_grid)
        elif isinstance(dist_grid, numbers.Number):
            return self.meters_per_grid_unit * dist_grid
        else:
            raise TypeError("Expected number or tuple of numbers")

    def remove(self, agent):
        self.grid.remove_agent(agent)
        self.scheduler.remove(agent)

    def get_agents(self, agent_type=None):
        if agent_type is None:
            return self.scheduler.agents
        else:
            return [agent for agent in self.scheduler.agents if isinstance(agent, agent_type)]
