import time
from .agent_name_mapping import agent_name_mapping
from .human import HumanAgent
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from simoc_server.database.db_model import AgentModelState, AgentState, AgentType, SnapshotBranch, \
                                    AgentModelSnapshot
from simoc_server import db
from uuid import uuid4

import threading

class AgentModel(object):

    def __init__(self, grid_width=None, grid_height=None, agent_model_state=None):
        # for testing
        agent_model_state = AgentModelState.query.order_by(AgentModelState.date_created).first()
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
        self.snapshot_branch = SnapshotBranch(name="root")
        db.session.add(self.snapshot_branch)
        db.session.commit()
        self.step_num = 0
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = MultiGrid(self.grid_width, self.grid_height, True)
        self.scheduler = RandomActivation(self)

        # for testing
        human_agent = HumanAgent(self)
        print("Created human agent: {0}".format(human_agent.energy))
        self.add_agent(human_agent, (0,0))
        human_agent = HumanAgent(self)
        print("Created human agent: {0}".format(human_agent.energy))
        self.add_agent(human_agent, (1,2))

    def add_agent(self, agent, pos):
        self.scheduler.add(agent)
        self.grid.place_agent(agent, pos)

    def num_agents(self):
        return len(self.schedule.agents)

    def set_snapshot_branch(self, session=None):
        # aquire snapshot branch and lock it
        if not session:
            session = db.create_scoped_session(options={
                "autocommit":False,
                "autoflush":True
                })

        def check_branch():
            aquired_snapshot_branch = session.query(SnapshotBranch).with_for_update(nowait=False) \
                .filter_by(id=self.snapshot_branch.id).first()
            if(aquired_snapshot_branch.save_lock):
                session.rollback()
                check_branch()
            else:
                # aquire lock
                aquired_snapshot_branch.save_lock = 1
                session.add(aquired_snapshot_branch)
                session.commit()

                for agent_model_snapshot in aquired_snapshot_branch.agent_model_snapshots:
                    if agent_model_snapshot.agent_model_state.step_num >= self.step_num:
                        aquired_snapshot_branch.save_lock = 0
                        session.add(aquired_snapshot_branch)
                        session.commit()
                        aquired_snapshot_branch = SnapshotBranch(name="{0}.{1}".format(self.snapshot_branch.name, uuid4()),
                            parent_branch_id=self.snapshot_branch.id)
                        aquired_snapshot_branch.save_lock = 1
                        session.add(aquired_snapshot_branch)
                        session.commit()
                        break
                self.snapshot_branch = SnapshotBranch.query.filter_by(id=aquired_snapshot_branch.id).first()
                session.close()

        check_branch()          


    def snapshot(self):
        self.set_snapshot_branch()
        try:
            agent_model_state = AgentModelState(step_num=self.step_num, grid_width=self.grid.width, grid_height=self.grid.height)
            snapshot = AgentModelSnapshot(agent_model_state=agent_model_state, snapshot_branch=self.snapshot_branch)
            db.session.add(agent_model_state)
            db.session.add(snapshot)
            for agent in self.scheduler.agents:
                agent.snapshot(agent_model_state, commit=False)
            db.session.commit()
            return snapshot

        finally:
            self.snapshot_branch.save_lock = 0
            db.session.add(self.snapshot_branch)
            db.session.commit()

    def step(self):
        self.step_num += 1