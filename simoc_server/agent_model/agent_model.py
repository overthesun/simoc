import time
import numbers
import threading
import datetime
import numpy as np
import functools
import operator
from abc import ABCMeta, abstractmethod
from uuid import uuid4

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from sqlalchemy.orm.exc import StaleDataError

from simoc_server.database.db_model import AgentModelState, AgentState, \
    AgentType, AgentModelSnapshot, SnapshotBranch, AgentModelParam

from simoc_server import db
from simoc_server.agent_model import agents
from simoc_server.util import sum_attributes


class AgentModel(Model):

    def __init__(self, init_params):
        self.load_params()

        self.grid_width = init_params.grid_width
        self.grid_height = init_params.grid_height
        self.model_time = init_params.starting_model_time
        self.snapshot_branch = init_params.snapshot_branch
        self.seed = init_params.seed
        self.random_state = init_params.random_state

        self.atmospheres = []
        self.plumbing_systems = []

        # if no random state given, initialize a new one
        if self.random_state is None:
            # if no random seed given initialize a new one
            if self.seed is None:
                self.seed = int(np.random.randint(2**32, dtype='int64'))
            self.random_state = np.random.RandomState(self.seed)

        if not isinstance(self.seed, int):
            raise Exception("Seed value must be of type 'int', got type '{}'".format(type(self.seed)))
        self.grid = MultiGrid(self.grid_width, self.grid_height, True, random_state=self.random_state)
        self.scheduler = RandomActivation(self, random_state=self.random_state)

        self.scheduler.steps = init_params.starting_step_num

    @property
    def total_water(self):
        return sum_attributes(self.plumbing_systems, "water")

    @property
    def total_waste_water(self):
        return sum_attributes(self.plumbing_systems, "waste_water")

    @property
    def total_oxygen(self):
        return sum_attributes(self.atmospheres, "oxygen")

    @property
    def total_carbon_dioxide(self):
        return sum_attributes(self.atmospheres, "carbon_dioxide")

    @property
    def total_nitrogen(self):
        return sum_attributes(self.atmospheres, "nitrogen")

    @property
    def total_argon(self):
        return sum_attributes(self.atmospheres, "argon")

    @property
    def step_num(self):
        return self.scheduler.steps

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
        model_time = agent_model_state.model_time
        seed = agent_model_state.seed
        random_state = agent_model_state.random_state

        init_params = AgentModelInitializationParams()

        (init_params.set_grid_width(grid_width)
                    .set_grid_height(grid_height)
                    .set_starting_step_num(step_num)
                    .set_starting_model_time(model_time)
                    .set_snapshot_branch(snapshot_branch)
                    .set_seed(seed)
                    .set_random_state(random_state))

        model = AgentModel(init_params)

        for agent_state in agent_model_state.agent_states:
            agent_type_name = agent_state.agent_type.name
            agent_class = agents.get_agent_by_type_name(agent_type_name)
            agent = agent_class(model, agent_state)
            model.add_agent(agent)
            print("Loaded {0} agent from db {1}".format(agent_type_name, agent.status_str()))

        for agent in model.get_agents():
            agent.post_db_load()

        return model

    @classmethod
    def create_new(cls, model_init_params, agent_init_recipe):
        model = AgentModel(model_init_params)
        agent_init_recipe.init_agents(model)
        return model

    @classmethod
    def create_atmosphere(cls, model, structures):
        atmosphere = agents.Atmosphere(model)

        atmosphere.temp = model.initial_temp
        atmosphere.oxygen = model.initial_oxygen
        atmosphere.carbon_dioxide = model.initial_carbon_dioxide
        atmosphere.nitrogen = model.initial_nitrogen
        atmosphere.argon = model.initial_argon

        for structure in structures:
            structure.set_atmosphere(atmosphere, maintain_pressure=True)

        return atmosphere

    @classmethod
    def create_plumbing_system(cls, model, structures):
        plumbing_system = agents.PlumbingSystem(model)
        plumbing_system.water = model.initial_water
        plumbing_system.waste_water = model.initial_waste_water

        for structure in structures:
            structure.set_plumbing_system(plumbing_system)

        return plumbing_system

    def add_agent(self, agent, pos=None):
        if pos is None and hasattr(agent, "pos"):
            pos = agent.pos
        self.scheduler.add(agent)
        if pos is not None:
            self.grid.place_agent(agent, pos)

        if isinstance(agent, agents.Atmosphere):
            self.atmospheres.append(agent)
        elif isinstance(agent, agents.PlumbingSystem):
            self.plumbing_systems.append(agent)

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
            agent_model_state = AgentModelState(step_num=self.step_num, grid_width=self.grid.width,
                    grid_height=self.grid.height, model_time=self.model_time, seed=self.seed,
                    random_state=self.random_state)
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
        self.model_time += self.timedelta_per_step()
        self.scheduler.step()
        print("{0} step_num {1}".format(self, self.step_num))
        print("o2: {} co2: {} n2: {} ar: {} h2o: {} waste_h2o: {}".format(
            self.total_oxygen, self.total_carbon_dioxide, self.total_nitrogen,
            self.total_argon, self.total_water, self.total_waste_water))

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
        self.scheduler.remove(agent)
        if hasattr(agent, "pos"):
            self.grid.remove_agent(agent)

        if isinstance(agent, agents.Atmosphere):
            self.atmospheres.remove(agent)
        elif isinstance(agent, agents.PlumbingSystem):
            self.plumbing_systems.remove(agent)

    def get_agents(self, agent_type=None):
        if agent_type is None:
            return self.scheduler.agents
        else:
            return [agent for agent in self.scheduler.agents if isinstance(agent, agent_type)]

    def agent_by_id(self, unique_id):
        for agent in self.get_agents():
            if(agent.unique_id == unique_id):
                return agent
        return None

class AgentModelInitializationParams(object):

    snapshot_branch = None
    seed = None
    random_state = None
    starting_step_num = 0

    def set_grid_width(self, grid_width):
        self.grid_width = grid_width
        return self

    def set_grid_height(self, grid_height):
        self.grid_height = grid_height
        return self

    def set_starting_step_num(self, starting_step_num):
        self.starting_step_num = starting_step_num
        return self

    def set_starting_model_time(self, starting_model_time):
        self.starting_model_time = starting_model_time
        return self

    def set_snapshot_branch(self, snapshot_branch):
        self.snapshot_branch = snapshot_branch
        return self

    def set_seed(self, seed):
        self.seed = seed
        return self

    def set_random_state(self, random_state):
        self.random_state = random_state
        return self

class AgentInitializerRecipe(metaclass=ABCMeta):

    @abstractmethod
    def init_agents(self, model):
        pass


class DefaultAgentInitializerRecipe(AgentInitializerRecipe):

    def init_agents(self, model):
        crew_quarters = agents.CrewQuarters(model)
        model.add_agent(crew_quarters, (0,0))

        atmosphere = AgentModel.create_atmosphere(model, [crew_quarters])
        plumbing_system = AgentModel.create_plumbing_system(model, [crew_quarters])
        model.add_agent(atmosphere)
        model.add_agent(plumbing_system)
        for i in range(4):
            human_agent = agents.HumanAgent(model, structure=crew_quarters)
            model.add_agent(human_agent)

        return model