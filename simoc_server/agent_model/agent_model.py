r"""Describes Agent Model interface and behaviour,
"""

import datetime
import json
import random
from abc import ABCMeta, abstractmethod

import numpy as np
import quantities as pq
from mesa import Model
from mesa.time import RandomActivation
from sqlalchemy.orm.exc import StaleDataError

from simoc_server import db, app
from simoc_server.agent_model.agents.core import GeneralAgent, StorageAgent
from simoc_server.agent_model.attribute_meta import AttributeHolder
from simoc_server.database.db_model import AgentModelParam, AgentType, AgentModelState, \
    AgentModelSnapshot, SnapshotBranch, CurrencyType
from simoc_server.util import timedelta_to_hours, location_to_day_length_minutes
from simoc_server.exceptions import AgentModelInitializationError
from simoc_server.agent_model.parse_data_files import parse_agent_desc

class PrioritizedRandomActivation(RandomActivation):
    """A custom step scheduler for MESA prioritized by agent class."""

    def __init__(self, model):
        """Creates a MESA agent scheduler object.

        A scheduler manages agent activations for each time step. This class performs step method
        execution of all agents in the predefined order based on their classes. All activations
        within a single class are scheduled randomly. This provides an ability to prioritize
        currency exchange for specific classes of agents (e.g. humans).

        Args:
          model: mesa.Model, MESA model to manage
        """
        self.agents_by_class = {}
        self.initialized = False
        super(RandomActivation, self).__init__(model)

    def step(self):
        if not self.initialized:
            self._load_agents_by_class()
        for agent_class in self.model.priorities:
            if agent_class in self.agents_by_class:
                agents = self.agents_by_class[agent_class]
                self.model.random_state.shuffle(agents)
                for agent in agents[:]:
                    agent.step()
        self.steps += 1
        self.time += 1

    def _load_agents_by_class(self):
        for agent in self.agents[:]:
            agent_class = agent.agent_class
            if agent_class not in self.agents_by_class:
                self.agents_by_class[agent_class] = []
            self.agents_by_class[agent_class].append(agent)
        self.initialized = True


class AgentModel(Model, AttributeHolder):
    """The core class that describes the SIMOC's Agent Model interface.

    The class stores and manages a stateful representation of a single SIMOC simulation and takes
    care of all agent management and orchestration, model initialization, persistence and
    monitoring.

    Attributes:
          config: int,
          day_length_hours: int,
          day_length_minutes: int,
          daytime: int,
          is_terminated: int,
          location: int,
          minutes_per_step: int,
          storage_ratios: Dict,
          priorities: int,
          random_state: int,
          scheduler: int,
          seed: int,
          single_agent: int,
          snapshot_branch: int,
          termination: int,
          time: int,
    """

    def __init__(self, init_params):
        """Creates an Agent Model object.

        TODO

        Args:
          init_params: AgentModelInitializationParams, TODO
        """
        super(Model, self).__init__()
        self.currency_dict = (init_params.currencies)
        self.start_time = None
        self.game_id = None
        self.user_id = None
        self.snapshot_branch = init_params.snapshot_branch
        self.seed = init_params.seed
        self.random_state = init_params.random_state
        self.termination = init_params.termination
        self.termination_reason = None
        self.single_agent = init_params.single_agent
        self.priorities = init_params.priorities
        self.location = init_params.location
        self.config = init_params.config
        self.time = init_params.starting_model_time
        self.minutes_per_step = init_params.minutes_per_step
        self.is_terminated = False
        self.storage_ratios = {}
        self.step_records_buffer = []
        self.day_length_minutes = location_to_day_length_minutes(self.location)
        self.day_length_hours = self.day_length_minutes / 60
        self.daytime = int(self.time.total_seconds() / 60) % self.day_length_minutes
        if self.seed is None:
            self.seed = random.getrandbits(32)
        if self.random_state is None:
            self.random_state = np.random.RandomState(self.seed)
        if self.priorities:
            self.scheduler = PrioritizedRandomActivation(self)
        else:
            self.scheduler = RandomActivation(self)
        self.scheduler.steps = init_params.starting_step_num

    @property
    def logger(self):
        """Returns Flask logger object."""
        return app.logger

    def get_step_logs(self):
        """TODO

        Called from:
            game_runner.py GameRunner.step_to.step_loop

        Returns
        """
        record_id = random.getrandbits(63)
        model_record = dict(id=record_id,
                            step_num=self.step_num,
                            user_id=self.user_id,
                            game_id=self.game_id,
                            start_time=self.start_time,
                            time=self["time"].total_seconds(),
                            hours_per_step=timedelta_to_hours(self.timedelta_per_step()),
                            is_terminated=str(self.is_terminated),
                            termination_reason=self.termination_reason)
        agent_type_counts = []
        for key, counter in self.get_agent_type_counts().items():
            agent_type, agent_type_id = key.split('#')
            agent_type_count_record = dict(game_id=self.game_id,
                                           user_id=self.user_id,
                                           step_num=self.step_num,
                                           agent_type=agent_type,
                                           agent_type_id=agent_type_id,
                                           agent_counter=counter)
            agent_type_counts.append(agent_type_count_record)
        storage_capacities = []
        for storage in self.get_storage_capacities():
            for currency in storage['currencies']:
                storage_capacity_record = dict(game_id=self.game_id,
                                               user_id=self.user_id,
                                               step_num=self.step_num,
                                               storage_id=storage['storage_id'],
                                               storage_amount=storage['amount'],
                                               storage_agent_id=storage['storage_agent_id'],
                                               storage_type=storage['agent_type'],
                                               storage_type_id=storage['agent_type_id'],
                                               currency_type=currency['currency_type'],
                                               currency_type_id=currency['currency_type_id'],
                                               value=currency['value'],
                                               capacity=currency['capacity'],
                                               unit=currency['units'])
                storage_capacities.append(storage_capacity_record)
        return model_record, agent_type_counts, storage_capacities

    def get_agent_type_counts(self):
        """TODO

        TODO

        Returns:
          TODO
        """
        counter = {}
        for agent in self.get_agents_by_role(role="flows"):
            agent_type = agent.agent_type
            agent_type_id = agent.agent_type_id
            key = f'{agent_type}#{agent_type_id}'
            if key not in counter:
                counter[key] = 0
            counter[key] += 1 * agent.amount
        return counter

    def get_storage_capacities(self, value_round=6):
        """TODO

        Formats the agent storages and currencies for easier access to the step information later.

        Returns:
          A dictionary of the storages information for this step
        """
        storages = []
        for storage in self.get_agents_by_role(role="storage"):
            entity = {"agent_type": storage.agent_type,
                      "agent_type_id": storage.agent_type_id,
                      "storage_agent_id": storage.unique_id,
                      "storage_id": storage.id,
                      "amount": storage.amount,
                      "currencies": []}
            for attr in storage.attrs:
                if attr.startswith('char_capacity'):
                    currency_name = attr.split('_', 2)[2]
                    currency_data = self.currency_dict[currency_name]
                    entity["currencies"].append({"currency_type": currency_data['name'],
                                                 "currency_type_id": currency_data['id'],
                                                 "value": round(storage[currency_name], value_round),
                                                 "units": storage.attr_details[attr]['units'],
                                                 "capacity": storage.attrs[attr]})
            storages.append(entity)
        return storages

    @property
    def step_num(self):
        """Returns the last step number."""
        return self.scheduler.steps

    @classmethod
    def load_from_db(cls, agent_model_state):
        """TODO

        TODO

        Args:
            agent_model_state: simoc_server.database.db_model.AgentModelState, Agent model state to
                load the game runner from.

        Returns:
          TODO
        """
        snapshot_branch = agent_model_state.agent_model_snapshot.snapshot_branch
        step_num = agent_model_state.step_num
        model_time = agent_model_state.model_time
        seed = agent_model_state.seed
        random_state = agent_model_state.random_state
        minutes_per_step = agent_model_state.minutes_per_step
        location = agent_model_state.location
        termination = json.loads(agent_model_state.termination)
        priorities = json.loads(agent_model_state.priorities)
        config = json.loads(agent_model_state.config)
        init_params = AgentModelInitializationParams()
        (init_params.set_starting_step_num(step_num)
         .set_starting_model_time(model_time)
         .set_snapshot_branch(snapshot_branch)
         .set_seed(seed)
         .set_random_state(random_state)
         .set_termination(termination)
         .set_priorities(priorities)
         .set_minutes_per_step(minutes_per_step)
         .set_location(location)
         .set_config(config))
        model = AgentModel(init_params)
        agents = {}
        for agent_state in agent_model_state.agent_states:
            agent_class = agent_state.agent_type.agent_class
            if agent_class not in agents:
                agents[agent_class] = []
            agents[agent_class].append({"agent_type": agent_state.agent_type.name,
                                        "unique_id": agent_state.agent_unique_id,
                                        "model_time_created": agent_state.model_time_created,
                                        "id": agent_state.agent_id,
                                        "active": agent_state.active,
                                        "age": agent_state.age,
                                        "amount": agent_state.amount,
                                        "lifetime": agent_state.lifetime,
                                        "connections": json.loads(agent_state.connections),
                                        "buffer": json.loads(agent_state.buffer),
                                        "deprive": json.loads(agent_state.deprive),
                                        "attributes": json.loads(agent_state.attributes)})
        for storage in agents['storage']:
            agent = StorageAgent(model=model, **storage)
            for attr in storage['attributes']:
                agent[attr['name']] = attr['value']
            model.add_agent(agent)
        _ = agents.pop('storage')
        for agent_class in agents:
            for agent in agents[agent_class]:
                new_agent = GeneralAgent(model=model, **agent)
                for attr in agent['attributes']:
                    new_agent[attr['name']] = attr['value']
                model.add_agent(new_agent)
        return model

    @classmethod
    def create_new(cls, model_init_params, agent_init_recipe):
        """TODO

        TODO

        Args:
            model_init_params: TODO
            agent_init_recipe: TODO

        Returns:
          TODO
        """
        model = AgentModel(model_init_params)
        agent_init_recipe.init_agents(model)
        return model

    def add_agent(self, agent):
        """TODO

        TODO

        Args:
            agent: TODO
        """
        self.scheduler.add(agent)

    def num_agents(self):
        """Returns total number of agents in the models."""
        return len(self.schedule.agents)

    def _branch(self):
        """TODO"""
        self.snapshot_branch = SnapshotBranch(parent_branch_id=self.snapshot_branch.id)

    def snapshot(self):
        """TODO

        TODO

        Args:

        Returns:
          TODO
        """
        if self.snapshot_branch is None:
            self.snapshot_branch = SnapshotBranch()
        else:
            if self.snapshot_branch.version_id is not None:
                self.snapshot_branch.version_id += 1
        try:
            last_saved_branch_state = AgentModelState.query \
                .join(AgentModelSnapshot) \
                .join(SnapshotBranch, SnapshotBranch.id == self.snapshot_branch.id) \
                .order_by(AgentModelState.step_num.desc()) \
                .limit(1) \
                .first()
            if (last_saved_branch_state is not None and
                    last_saved_branch_state.step_num >= self.step_num):
                self._branch()
            agent_model_state = AgentModelState(step_num=self.step_num,
                                                model_time=self.time,
                                                seed=self.seed,
                                                random_state=self.random_state,
                                                minutes_per_step=self.minutes_per_step,
                                                termination=json.dumps(self.termination),
                                                priorities=json.dumps(self.priorities),
                                                location=self.location,
                                                config=json.dumps(self.config))
            snapshot = AgentModelSnapshot(agent_model_state=agent_model_state,
                                          snapshot_branch=self.snapshot_branch)
            try:
                db.session.add(agent_model_state)
                db.session.add(snapshot)
                db.session.add(self.snapshot_branch)
                for agent in self.scheduler.agents:
                    agent.snapshot(agent_model_state)
                db.session.commit()
            except:
                app.logger.exception('Failed to save a game.')
                db.session.rollback()
            finally:
                db.session.close()
            return snapshot
        except StaleDataError:
            app.logger.warning("WARNING: StaleDataError during snapshot, probably a simultaneous"
                               "save, changing branch.")
            db.session.rollback()
            self._branch()
            return self.snapshot()

    def step(self):
        """TODO

        TODO
        """
        self.time += self.timedelta_per_step()
        self.daytime = int(self.time.total_seconds() / 60) % self.day_length_minutes
        # Check termination conditions; stop if true
        for cond in self.termination:
            if cond['condition'] == "time":
                value = cond['value']
                unit = cond['unit']
                model_time = self.time.total_seconds()
                if unit == 'min':
                    model_time /= 60
                elif unit == 'hour':
                    model_time /= 3600
                elif unit == 'day':
                    model_time /= 3600 * self.day_length_hours
                elif unit == 'year':
                    model_time /= 3600 * self.day_length_hours * 365
                else:
                    model_time /= 3600 * self.day_length_hours
                if model_time > value:
                    self.is_terminated = True
                    self.termination_reason = 'time'
                    return
        # Step agents
        self.scheduler.step()
        app.logger.info("{0} step_num {1}".format(self, self.step_num))

    def timedelta_per_step(self):
        """TODO"""
        return datetime.timedelta(minutes=self.minutes_per_step)

    def remove(self, agent):
        """TODO"""
        self.scheduler.remove(agent)

    def get_agents_by_type(self, agent_type=None):
        """TODO

        TODO

        Args:
            agent_type: TODO

        Returns:
          TODO
        """
        if agent_type is None:
            return self.scheduler.agents
        else:
            return [agent for agent in self.scheduler.agents if agent.agent_type == agent_type]

    def get_agents_by_class(self, agent_class=None):
        """TODO

        TODO

        Args:
            agent_class: TODO

        Returns:
          TODO
        """
        if agent_class is None:
            return self.scheduler.agents
        else:
            return [agent for agent in self.scheduler.agents if isinstance(agent, agent_class)]

    def agent_by_id(self, id):
        """TODO

        TODO

        Args:
            id: TODO

        Returns:
          TODO
        """
        for agent in self.get_agents_by_type():
            if agent.id == id:
                return agent
        return None

    def get_agents_by_role(self, role=None):
        if role == 'storage':
            return [agent for agent in self.scheduler.agents if agent.has_storage]
        elif role == 'flows':
            return [agent for agent in self.scheduler.agents if agent.has_flows]

class AgentModelInitializationParams(object):
    """TODO

    TODO

    Attributes:
          snapshot_branch: TODO
          seed: TODO
          random_state: TODO
          starting_step_num: TODO
          single_agent: TODO
          minutes_per_step: TODO
          termination: TODO
          priorities: TODO
          location: TODO
          config: TODO
          currencies: TODO
    """
    snapshot_branch = None
    seed = None
    random_state = None
    starting_step_num = 0
    single_agent = 0
    minutes_per_step = 60
    termination = []
    priorities = []
    location = 'mars'
    config = {}
    currencies = {}

    def set_currencies(self, currencies):
        """TODO

        TODO

        Args:
            currencies: TODO

        Returns:
          TODO
        """
        self.currencies = currencies
        return self

    def set_starting_step_num(self, starting_step_num):
        """TODO

        TODO

        Args:
            starting_step_num: TODO

        Returns:
          TODO
        """
        self.starting_step_num = starting_step_num
        return self

    def set_starting_model_time(self, starting_model_time):
        """TODO

        TODO

        Args:
            starting_model_time: TODO

        Returns:
          TODO
        """
        self.starting_model_time = starting_model_time
        return self

    def set_snapshot_branch(self, snapshot_branch):
        """TODO

        TODO

        Args:
            snapshot_branch: TODO

        Returns:
          TODO
        """
        self.snapshot_branch = snapshot_branch
        return self

    def set_seed(self, seed):
        """TODO

        TODO

        Args:
            seed: TODO

        Returns:
          TODO
        """
        self.seed = seed
        return self

    def set_random_state(self, random_state):
        """TODO

        TODO

        Args:
            random_state: TODO

        Returns:
          TODO
        """
        self.random_state = random_state
        return self

    def set_single_agent(self, single_agent):
        """TODO

        TODO

        Args:
            single_agent: TODO

        Returns:
          TODO
        """
        self.single_agent = single_agent
        return self

    def set_termination(self, termination):
        """TODO

        TODO

        Args:
            termination: TODO

        Returns:
          TODO
        """
        self.termination = termination
        return self

    def set_priorities(self, priorities):
        """TODO

        TODO

        Args:
            priorities: TODO

        Returns:
          TODO
        """
        self.priorities = priorities
        return self

    def set_minutes_per_step(self, minutes_per_step):
        """TODO

        TODO

        Args:
            minutes_per_step: TODO

        Returns:
          TODO
        """
        self.minutes_per_step = minutes_per_step
        return self

    def set_location(self, location):
        """TODO

        TODO

        Args:
            location: TODO

        Returns:
          TODO
        """
        self.location = location
        return self

    def set_config(self, config):
        """TODO

        TODO

        Args:
            config: TODO

        Returns:
          TODO
        """
        self.config = config
        return self


class AgentInitializerRecipe(metaclass=ABCMeta):
    """TODO"""

    @abstractmethod
    def init_agents(self, model):
        """TODO"""
        pass


class BaseLineAgentInitializerRecipe(AgentInitializerRecipe):
    """TODO

    TODO

    Attributes:
          AGENTS: TODO
          STORAGES: TODO
          SINGLE_AGENT: TODO
          AGENT_LIST: TODO
    """

    def __init__(self, config, currencies, agent_desc):
        """Creates an Agent Initializer object.

        TODO

        Args:
          config: Dict, TODO
        """
        self.AGENT_DESC = parse_agent_desc(config, currencies, agent_desc)
        self.AGENTS = config['agents']
        self.SINGLE_AGENT = config['single_agent']

    def init_agents(self, model):
        """TODO

        TODO

        Args:
            model: TODO

        Returns:
          TODO
        """
        for type_name, instance in self.AGENTS.items():
            agent_desc = self.AGENT_DESC.get(type_name, None)
            if not agent_desc:
                raise AgentModelInitializationError("agent_desc data not found for {type_name}.")
            connections = instance.pop('connections') if 'connections' in instance else {}
            amount = instance.pop('amount') if 'amount' in instance else 1
            if self.SINGLE_AGENT == 1:
                model.add_agent(GeneralAgent(model=model,
                                             agent_type=type_name,
                                             agent_desc=agent_desc,
                                             connections=connections,
                                             amount=amount,
                                             **instance))
            else:
                for i in range(amount):
                    model.add_agent(GeneralAgent(model=model,
                                                 agent_desc=agent_desc,
                                                 agent_type=type_name,
                                                 connections=connections,
                                                 amount=1,
                                                 **instance))

        # The '_init_selected_storage' method takes the connections dict,
        # supplied above, and makes a connection to the actual agent object
        # in the model. Because agents have connections to other agents, all
        # must be initialized before connections can be made.
        for agent in model.get_agents_by_role(role="flows"):
            agent._init_selected_storage()

        return model
