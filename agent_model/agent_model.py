r"""Describes Agent Model interface and behaviour,
"""

import random
import datetime
from abc import ABCMeta, abstractmethod

import numpy as np
from mesa import Model
from mesa.time import RandomActivation

# from simoc_server import app  # TODO: Fix logger
from agent_model.initializer import AgentModelInitializer
from agent_model.agents.core import GeneralAgent
from agent_model.agents.data_collector import AgentDataCollector
from agent_model.attribute_meta import AttributeHolder
from agent_model.util import timedelta_to_hours, location_to_day_length_minutes
from agent_model.exceptions import AgentModelInitializationError

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

    @classmethod
    def from_config(cls, config, currency_desc=None, agent_desc=None, connections=None):
        """Takes configuration files, return an initialized model

        Args (required):
            config          dict    A properly-formatted config object

        Kwargs (optional):
            currency_desc   dict    User-specified currencies
            agent_desc      dict    User-specified agents
            agent_conn      dict    User-specified connections
        """
        initializer = AgentModelInitializer.from_new(config, currency_desc, agent_desc, connections)
        return cls(initializer)

    def save(self):
        """Exports current model as an AgentModelInitializer"""
        initializer = AgentModelInitializer.from_model(self)
        return initializer.serialize()

    @classmethod
    def load(cls, saved):
        """Takes a save file and returns an initialized AgentModel"""
        initializer = AgentModelInitializer.deserialize(saved)
        return cls(initializer)

    def __init__(self, initializer):
        """Creates an Agent Model object.

        Args:
          initializer: AgentModelInitializer, contains all setup data
        """
        super(Model, self).__init__()
        #------------------------------
        #    INITIALIZE MODEL DATA
        #------------------------------
        md = initializer.model_data
        # Metadata (optional, set externally)
        self.user_id = md.get('user_id', None)
        self.game_id = md.get('game_id', None)
        self.start_time = md.get('start_time', None)
        # Configuration (user-input)
        self.seed = md['seed']
        self.global_entropy = md.get('global_entropy', None)
        self.single_agent = md['single_agent']
        self.termination = md['termination']
        self.priorities = md['priorities']
        self.location = md.get('location')
        self.total_amount = md['total_amount']
        self.minutes_per_step = md['minutes_per_step']
        self.currency_dict = md['currency_dict']
        # Status (generated when model is initialized, saved)
        if initializer.init_type == 'from_new':
            self.random_state = np.random.RandomState(self.seed)
            self.time = datetime.timedelta()
            self.starting_step_num = 0
            self.storage_ratios = {}
            self.step_records_buffer = []
            self.is_terminated = False
            self.termination_reason = None
        elif initializer.init_type == 'from_model':
            self.random_state = np.random.RandomState()
            self.random_state.set_state(md.get('random_state'))
            self.time = eval(md['time'])
            self.starting_step_num = md['steps']
            self.storage_ratios = md['storage_ratios']
            self.step_records_buffer = md['step_records_buffer']
            self.is_terminated = md['is_terminated']
            self.termination_reason = md['termination_reason']
        else:
            raise AgentModelInitializationError(f"Unrecognized initializer type: {initializer.init_type}")
        # Calculated / Temporary
        if self.priorities:
            self.scheduler = PrioritizedRandomActivation(self)
        else:
            self.scheduler = RandomActivation(self)
        self.scheduler.steps = self.starting_step_num
        self.day_length_minutes = location_to_day_length_minutes(self.location)
        self.day_length_hours = self.day_length_minutes / 60
        self.daytime = int(self.time.total_seconds() / 60) % self.day_length_minutes
        self.timedelta_per_step = datetime.timedelta(minutes=self.minutes_per_step)
        self.hours_per_step = timedelta_to_hours(self.timedelta_per_step)

        #------------------------------
        #     INITIALIZE AGENT DATA
        #------------------------------
        for agent_type, agent_data in initializer.agent_data.items():
            agent_desc, instance = agent_data.values()
            connections = instance.pop('connections', {})
            amount = instance.pop('amount', 1)
            if self.single_agent == 1:
                agent = GeneralAgent(model=self,
                                     agent_type=agent_type,
                                     agent_desc=agent_desc,
                                     connections=connections,
                                     amount=amount,
                                     **instance)
                self.scheduler.add(agent)
            else:
                for i in range(amount):
                    agent = GeneralAgent(model=self,
                                         agent_desc=agent_desc,
                                         agent_type=agent_type,
                                         connections=connections,
                                         amount=1,
                                         **instance)
                    self.scheduler.add(agent)
        for agent in self.scheduler.agents:
            agent._init_currency_exchange()
            agent.data_collector = AgentDataCollector.from_agent(agent)

    # TODO: Fix logger
    # @property
    # def logger(self):
    #     """Returns Flask logger object."""
    #     return app.logger

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
                            hours_per_step=self.hours_per_step,
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
                                               unit=currency['unit'])
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
                                                 "unit": storage.attr_details[attr]['unit'],
                                                 "capacity": storage.attrs[attr]})
            storages.append(entity)
        return storages

    @property
    def step_num(self):
        """Returns the last step number."""
        return self.scheduler.steps

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

    def step(self):
        """TODO

        TODO
        """
        self.time += self.timedelta_per_step
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
        for agent in self.scheduler.agents:
            agent.data_collector.step()
        # app.logger.info("{0} step_num {1}".format(self, self.step_num))  # TODO: Fix logger

    def step_to(self, n_steps=None, termination=None, timeout=365*24):
        if not n_steps and not termination:
            return
        for i in range(timeout):
            if i == n_steps:
                return
            elif self.is_terminated:
                return
            else:
                self.step()

    def get_data(self, debug=False, clear_cache=False):
        data = {}
        for agent in self.scheduler.agents:
            data[agent.agent_type] = agent.data_collector.get_data(debug, clear_cache)
        return data

    def remove(self, agent):
        """TODO"""
        # self.scheduler.remove(agent)

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
                for agent in agents:
                    agent.step()
        self.steps += 1
        self.time += 1

    def _load_agents_by_class(self):
        for agent in self.agents:
            agent_class = agent.agent_class
            if agent_class not in self.agents_by_class:
                self.agents_by_class[agent_class] = []
            self.agents_by_class[agent_class].append(agent)
        self.initialized = True

