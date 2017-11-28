import time
from .agent_name_mapping import agent_name_mapping
from . import HumanAgent
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from simoc_server.database.db_model import AgentModelState, AgentState, AgentType, AgentModelSnapshot, SnapshotBranch
from simoc_server import db
from uuid import uuid4
from sqlalchemy.orm.exc import StaleDataError

import threading

class AgentModel(object):

    def __init__(self, grid_width=None, grid_height=None, agent_model_state=None):
        if agent_model_state is not None:
            self.load_from_db(agent_model_state)
        else:
            self.init_new(grid_width ,grid_height)

    def load_from_db(self, agent_model_state):
        self.grid_width = agent_model_state.grid_width
        self.grid_height = agent_model_state.grid_height
        self.step_num = agent_model_state.step_num
        self.grid = MultiGrid(self.grid_width, self.grid_height, True)
        self.scheduler = RandomActivation(self)

        for agent_state in agent_model_state.agent_states:
            agent_type_name = agent_state.agent_type.name
            agent_class = agent_name_mapping[agent_type_name]
            agent = agent_class(self, agent_state)
            self.add_agent(agent, agent.pos)
            print("Loaded {0} agent from db {1}".format(agent_type_name, agent.status_str()))
        self.snapshot_branch = agent_model_state.agent_model_snapshot.snapshot_branch

    def init_new(self, grid_width, grid_height):
        self.snapshot_branch = None
        self.step_num = 0
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = MultiGrid(self.grid_width, self.grid_height, True)
        self.scheduler = RandomActivation(self)

        # for testing
        human_agent = HumanAgent(self)
        self.add_agent(human_agent, (0,0))
        human_agent = HumanAgent(self)
        self.add_agent(human_agent, (1,2))

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
        print("{0} step_num {1}".format(self, self.step_num))