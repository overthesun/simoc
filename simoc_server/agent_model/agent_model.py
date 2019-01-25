import numbers
import datetime
import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod

from mesa import Model
from mesa.time import RandomActivation, PrioritizedRandomActivation
from mesa.space import MultiGrid

from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy import or_

from simoc_server.database.db_model import AgentModelState, AgentModelSnapshot, SnapshotBranch, AgentModelParam, AgentType

from simoc_server.agent_model.agents.core import GeneralAgent, StorageAgent

from simoc_server.agent_model.attribute_meta import AttributeHolder

from simoc_server import db, app

from simoc_server.util import timedelta_to_hours

import quantities as pq

class AgentModel(Model, AttributeHolder):

    def __init__(self, init_params):
        self.load_params()
        self.grid_width = init_params.grid_width
        self.grid_height = init_params.grid_height
        self.snapshot_branch = init_params.snapshot_branch
        self.seed = init_params.seed
        self.random_state = init_params.random_state
        self.termination = init_params.termination
        self.logging = init_params.logging
        self.single_agent = init_params.single_agent
        self['time'] = init_params.starting_model_time
        self['is_terminated'] = False
        self.logs = []
        self.priorities = init_params.priorities
        self.config = init_params.configuration

        # if no random state given, initialize a new one
        if self.random_state is None:
            # if no random seed given initialize a new one
            if self.seed is None:
                self.seed = int(np.random.randint(2**32, dtype='int64'))
            self.random_state = np.random.RandomState(self.seed)

        if not isinstance(self.seed, int):
            raise Exception("Seed value must be of type 'int', got type '{}'".format(type(self.seed)))

        self.grid = MultiGrid(self.grid_width, self.grid_height, True, random_state=self.random_state)
        if self.priorities:
            self.scheduler = PrioritizedRandomActivation(self, random_state=self.random_state, priorities=self.priorities)
        else:
            self.scheduler = RandomActivation(self, random_state=self.random_state)
        self.scheduler.steps = getattr(init_params, "starting_step_num", 0)
        self.model_stats = {}


    @property
    def logger(self):
        return app.logger

    def get_logs(self, filters=[], columns=None, dtype='list'):
        df = pd.DataFrame(self.logs)
        for col, val in filters:
            df = df.loc[df[col].isin(val)].drop(col, axis=1)
        if columns:
            df = df.loc[:, columns]
        if dtype == 'list':
            return df.values.tolist()
        elif dtype == 'dict':
            return df.to_dict(orient='records')
        elif dtype == 'df':
            return df

    def get_step_logs(self, step_num, filters=[], columns=None, dtype='list'):
        return self.get_logs(filters=filters+[('step_num', [step_num])], columns=columns, dtype=dtype)

    def get_model_stats(self):
        response = {"step": self.step_num,
                    "hours_per_step": timedelta_to_hours(self.timedelta_per_step()),
                    "is_terminated": self['is_terminated'],
                    "time": self["time"].total_seconds(),
                    "agents": self.get_total_agents(),
                    "storages": self.get_total_storages(),
                    "model_stats": self.model_stats}
        if self.logging is not None:
            columns = self.logging.get('columns', [])
            filters = self.logging.get('filters', [])
            response["step_logs"] = self.get_step_logs(step_num=self.step_num - 1, columns=columns, filters=filters)
        if self['is_terminated']:
            response['termination_reason'] = self['termination_reason']
        return response

    def get_total_agents(self):
        timedelta_per_step = self.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        total_production, total_consumption, total_agent_types = {}, {}, {}
        for agent in self.get_agents_by_class(agent_class=GeneralAgent):
            agent_type = agent.agent_type
            if agent_type not in total_agent_types:
                total_agent_types[agent_type] = 0
            total_agent_types[agent_type] += 1
            for attr in agent.agent_type_attributes:
                prefix, currency = attr.split('_', 1)
                if prefix not in ['in', 'out']:
                    continue
                step_value = agent.get_step_value(attr, hours_per_step)
                if prefix == 'out':
                    if currency not in total_production:
                        total_production[currency] = step_value
                    else:
                        total_production[currency] += step_value
                elif prefix == 'in':
                    if currency not in total_consumption:
                        total_consumption[currency] = step_value
                    else:
                        total_consumption[currency] += step_value
                else:
                    raise Exception('Unknown flow type. Neither Input nor Output.')
        for k in total_consumption:
            if k in total_production:
                total_consumption[k].units = total_production[k].units
        return {"total_production": {k: {"value": "{:.4f}".format(v.magnitude.tolist()), "units": v.units.dimensionality.string} for k, v in total_production.items()},
                "total_consumption": {k: {"value": "{:.4f}".format(v.magnitude.tolist()), "units": v.units.dimensionality.string} for k, v in total_consumption.items()},
                "total_agent_types": total_agent_types}

    def get_total_storages(self):
        storages = []
        for storage in self.get_agents_by_class(agent_class=StorageAgent):
            entity = {"agent_type": storage.agent_type, "agent_id": storage.id, "currencies": []}
            for attr in storage.agent_type_attributes:
                if attr.startswith('char_capacity'):
                    currency = attr.split('_', 2)[2]
                    value = "{:.4f}".format(storage[currency])
                    capacity = storage.agent_type_attributes[attr]
                    storage_unit = storage.agent_type_descriptions[attr]
                    entity["currencies"].append({"name": currency, "value": value, "capacity": capacity, "units": storage_unit})
            storages.append(entity)
        return storages

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

    # def load_from_db(self, agent_model_state):
    #     snapshot_branch = agent_model_state.agent_model_snapshot.snapshot_branch
    #     grid_width = agent_model_state.grid_width
    #     grid_height = agent_model_state.grid_height
    #     step_num = agent_model_state.step_num
    #     model_time = agent_model_state.model_time
    #     seed = agent_model_state.seed
    #     random_state = agent_model_state.random_state
    #
    #     init_params = AgentModelInitializationParams()
    #
    #     (init_params.set_grid_width(grid_width)
    #                 .set_grid_height(grid_height)
    #                 .set_starting_step_num(step_num)
    #                 .set_starting_model_time(model_time)
    #                 .set_snapshot_branch(snapshot_branch)
    #                 .set_seed(seed)
    #                 .set_random_state(random_state))
    #
    #     model = AgentModel(init_params)
    #
    #     for agent_state in agent_model_state.agent_states:
    #         agent_type_name = agent_state.agent_type.name
    #         agent_class = agents.get_agent_by_type_name(agent_type_name)
    #         agent = agent_class(model, agent_state=agent_state)
    #         model.add_agent(agent)
    #         app.logger.info("Loaded {0} agent from db {1}".format(agent_type_name, agent.status_str()))
    #
    #     for agent in model.get_agents_by_type():
    #         agent.post_db_load()
    #
    #     self.create_alerts_watcher(model)
    #     return model

    @classmethod
    def create_new(cls, model_init_params, agent_init_recipe):
        model = AgentModel(model_init_params)
        agent_init_recipe.init_agents(model)
        return model

    def add_agent(self, agent, pos=None):
        if pos is None and hasattr(agent, "pos"):
            pos = agent.pos
        self.scheduler.add(agent)
        if pos is not None:
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
            agent_model_state = AgentModelState(step_num=self.step_num, grid_width=self.grid.width,
                    grid_height=self.grid.height, model_time=self['time'], seed=self.seed,
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
            app.logger.warning("WARNING: StaleDataError during snapshot, probably a simultaneous save, changing branch.")
            db.session.rollback()
            self._branch()
            return self.snapshot()

    def step(self):
        self['time'] += self.timedelta_per_step()
        self['daytime'] = int(self['time'].total_seconds() / 60) % (24 * 60)
        for cond in self.termination:
            if cond['condition'] == "time":
                value = cond['value']
                unit = cond['unit']
                model_time = self['time'].total_seconds()
                if unit == 'min':
                    model_time /= 60
                elif unit == 'hour':
                    model_time /= 3600
                elif unit == 'day':
                    model_time /= 86400
                elif unit == 'year':
                    model_time /= 31536000
                else:
                    raise Exception('Unknown termination time value.')
                if model_time > value:
                    self['is_terminated'] = True
                    self['termination_reason'] = 'time'
                    return
        for storage in self.get_agents_by_class(agent_class=StorageAgent):
            agent_id = '{}_{}'.format(storage.agent_type, storage.id)
            if agent_id not in self.model_stats:
                self.model_stats[agent_id] = {}
            temp, total = {}, None
            for attr in storage.agent_type_attributes:
                if attr.startswith('char_capacity'):
                    currency = attr.split('_', 2)[2]
                    storage_unit = storage.agent_type_descriptions[attr]
                    storage_value = pq.Quantity(float(storage[currency]), storage_unit)
                    if not total:
                        total = storage_value
                    else:
                        storage_value.units = total.units
                        total += storage_value
                    temp[currency] = storage_value.magnitude.tolist()
            for currency in temp:
                if temp[currency] > 0:
                    self.model_stats[agent_id][currency + '_ratio'] = temp[currency] / total.magnitude.tolist()
                else:
                    self.model_stats[agent_id][currency + '_ratio'] = 0
        self.scheduler.step()
        app.logger.info("{0} step_num {1}".format(self, self.step_num))

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

    def get_agents_by_type(self, agent_type=None):
        if agent_type is None:
            return self.scheduler.agents
        else:
            return [agent for agent in self.scheduler.agents if agent.agent_type == agent_type]

    def get_agents_by_class(self, agent_class=None):
        if agent_class is None:
            return self.scheduler.agents
        else:
            return [agent for agent in self.scheduler.agents if isinstance(agent, agent_class)]

    def agent_by_id(self, id):
        for agent in self.get_agents_by_type():
            if(agent.id == id):
                return agent
        return None

class AgentModelInitializationParams(object):

    snapshot_branch = None
    seed = None
    random_state = None
    starting_step_num = 0
    single_agent = 0


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

    def set_termination(self, termination):
        self.termination = termination
        return self

    def set_logging(self, logging):
        self.logging = logging
        return self

    def set_priorities(self, priorities):
        self.priorities = priorities
        return self

    def set_single_agent(self, single_agent):
        self.single_agent = single_agent
        return self

    def set_configuration(self, config):
        self.configuration = config
        return self

class AgentInitializerRecipe(metaclass=ABCMeta):

    @abstractmethod
    def init_agents(self, model):
        pass

class BaseLineAgentInitializerRecipe(AgentInitializerRecipe):

    def __init__(self, config):
        self.AGENTS = config['agents']
        self.STORAGES = config['storages']
        self.SINGLE_AGENT = config['single_agent']
        self.AGENT_LIST = [r for (r,) in db.session.query(AgentType.name).filter(or_(AgentType.agent_class == "plants", AgentType.agent_class == "power_generation"))]

    def init_agents(self, model):
        for type_name, instances in self.STORAGES.items():
            for instance in instances:
                model.add_agent(StorageAgent(model=model, agent_type=type_name, **instance))

        for type_name, instances in self.AGENTS.items():
            for instance in instances:
                connections, amount = instance["connections"], instance['amount']
                if(self.SINGLE_AGENT == 1 and type_name in self.AGENT_LIST):
                    amount = 1
                for i in range(amount):
                    model.add_agent(GeneralAgent(model=model, agent_type=type_name, connections=connections, amount=instance['amount']))

        return model
