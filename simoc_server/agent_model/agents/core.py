from abc import ABCMeta, abstractmethod
from mesa import Agent
from uuid import uuid4
import inspect

from simoc_server import db
from simoc_server.util import load_db_attributes_into_dict, extend_dict, NotLoaded
from simoc_server.database.db_model import AgentType, AgentState, AgentStateAttribute
from simoc_server.agent_model.attribute_meta import AttributeHolder

from simoc_server.util import timedelta_to_days, timedelta_to_hours, timedelta_hour_of_day

import quantities as pq

PERSISTABLE_ATTRIBUTE_TYPES = [int.__name__, float.__name__, str.__name__, type(None).__name__, 
    bool.__name__]

class BaseAgent(Agent, AttributeHolder, metaclass=ABCMeta):

    # Used to ensure type attributes are properly inherited and
    # only loaded once
    _last_loaded_type_attr_class = False


    def __init__(self, model, agent_type=None, agent_state=None):
        self.agent_type = agent_type
        # print('BaseAgent.init.agent_type: {}'.format(self.agent_type))
        self._load_agent_type_attributes()
        AttributeHolder.__init__(self)

        self.active = True
        if agent_state is not None:
            self.load_from_db(agent_state)
            super().__init__(self.unique_id, model)
        else:
            self.unique_id = "{0}_{1}".format(self.__class__.__name__, uuid4())
            self.model_time_created = model.model_time
            super().__init__(self.unique_id, model)

    def _load_agent_type_attributes(self):
        """ Load the agent type attributes from database into class.
            These agent type attributes should be static values that
            define the behaviors of a particular *class* of agents.
            They do not define instance level behavoirs or traits.

        Raises
        ------
        Exception
            If class does not define _agent_type_name or if the specified
            agent type cannot be located in the database
        """
        # print('1. cls = {}'.format(self))
        if self.agent_type is None:
            raise Exception("agent_type not set for class {}".format(self))

        if self._last_loaded_type_attr_class is not self:
            agent_type_name = self.agent_type
            # print('2. agent_type_name = {}'.format(agent_type_name))
            agent_type = AgentType.query.filter_by(name=agent_type_name).first()

            if agent_type is None:
                raise Exception("Cannot find agent_type in database with name '{0}'. Please"
                    " create associated AgentType and add to database".format(agent_type_name))

            attributes, descriptions = {}, {}
            try:
                load_db_attributes_into_dict(agent_type.agent_type_attributes, attributes, descriptions)
            except ValueError as e:
                raise ValueError("Error loading agent type attributes for class '{}'.".format(self.__name__)) from e

            self.agent_type_attributes, self.agent_type_descriptions = attributes, descriptions
            # print('BaseAgent._load_agent_type_attributes.attributes: {}'.format(attributes))
            # print('BaseAgent._load_agent_type_attributes.descriptions: {}'.format(descriptions))
            self._last_loaded_type_attr_class = self

            # store agent type id for later saving of agent state
            self._agent_type_id = agent_type.id

    def get_agent_type(self):
        """
        Returns
        -------
        AgentType
            Returns the AgentType related to the instance Agent
        """
        return AgentType.query.get(self.__class._agent_type_id)

    def get_agent_type_attribute(self, name):
        """ Get agent type attribute by name as it was defined in database

        Parameters
        ----------
        name : str
            The name of the attribute to return

        Returns
        -------
        Type of the Agent Attribute
            The value of the agent attribute with the given name
        """
        return self.agent_type_attributes[name]

    def load_from_db(self, agent_state):
        """ Load agent with the given state

        Parameters
        ----------
        agent_state : AgentState
            AgentState loaded from database to initialize the agent from
        """
        if agent_state.pos_x is not None and agent_state.pos_y is not None:
            self.pos = (agent_state.pos_x, agent_state.pos_y)
        self.unique_id = agent_state.agent_unique_id
        self.model_time_created = agent_state.model_time_created

        self.requires_post_load = {}

        try:
            load_db_attributes_into_dict(agent_state.agent_state_attributes, self.__dict__, load_later=[BaseAgent])
        except ValueError as e:
            raise ValueError("Error loading agent state attributes for class '{}'".format(self.__class__.__name__)) from e

    def post_db_load(self):
        for name, attribute_descriptor in self.attribute_descriptors.items():
            current_value = getattr(self, name)
            if issubclass(attribute_descriptor._type, BaseAgent) and isinstance(current_value, NotLoaded):
                id_value = current_value._db_raw_value
                # TODO remove check for str value 'None' and move it elsewhere, make better
                if id_value is not None:
                    if id_value == "None":
                        self.__dict__[name] = None
                    else:
                        self.__dict__[name] = self.model.agent_by_id(id_value)

    def snapshot(self, agent_model_state, commit=True):
        pos = self.pos if hasattr(self, "pos") else (None, None)
        agent_state = AgentState(agent_type_id=self.__class__._agent_type_id,
                 agent_model_state=agent_model_state, agent_unique_id=self.unique_id,
                 model_time_created=self.model_time_created, pos_x=pos[0], pos_y=pos[1])

        for attribute_name, attribute_descriptor in self.attribute_descriptors.items():
            if attribute_descriptor.is_persisted_attr:
                value = self.__dict__[attribute_name]
                value_type = attribute_descriptor._type
                is_agent_reference = False
                if issubclass(value_type, BaseAgent):
                    value_type_str = value_type.__module__ + "." + value_type.__name__
                    if value is not None:
                        value = value.unique_id
                    is_agent_reference = True
                else:
                    value_type_str =  value_type.__name__
                value_str = str(value)
                if value_type_str not in PERSISTABLE_ATTRIBUTE_TYPES and not is_agent_reference:
                    raise Exception("Attribute set to non-persistable type.")

                agent_state.agent_state_attributes.append(AgentStateAttribute(name=attribute_name, 
                    value=value_str, value_type=value_type_str))
        db.session.add(agent_state)
        if commit:
            db.session.commit()

    def status_str(self):
        sb = []
        for attribute_name, attribute_descriptor in self.attribute_descriptors.items():
            sb.append("{0}: {1}".format(attribute_name, self.__dict__[attribute_name]))
        return " ".join(sb)

    def destroy(self):
        self.active = False
        self.model.remove(self)


class EnclosedAgent(BaseAgent):

    def __init__(self, *args, **kwargs):
        self.agent_type = kwargs.get("agent_type", None)
        # print('EnclosedAgent.init.agent_type: {}'.format(self.agent_type))
        super(EnclosedAgent, self).__init__(*args, **kwargs)

    def step(self):
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        if 'age' not in self:
            self._attr('age', 0, is_client_attr=True, is_persisted_attr=True)
        else:
            self['age'] += hours_per_step / 24
        # print('age: {}'.format(self['age']))

        if 'char_lifetime' in self.agent_type_attributes:
            lifetime = self.agent_type_attributes['char_lifetime']
            if self['age'] >= lifetime:
                print('Lifetime limit has been reached by {}. Killing the agent'.format(self.agent_type))
                self.destroy('Lifetime limit reached')

    def destroy(self, reason):
        self.model.logger.info("Object Died! Reason: {}".format(reason))
        self.cause_of_death = reason
        super().destroy()

    def add_to_structure(self, target):
        if self.structure is not None:
            self.structure.remove_agent_from(self)
        target.place_agent_inside(self)
        self.structure = target

    def post_db_load(self):
        super().post_db_load()
        if self.structure is not None:
            self.structure.place_agent_inside(self)


class GeneralAgent(EnclosedAgent):

    def __init__(self, *args, **kwargs):
        self.agent_type = kwargs.get("agent_type", None)
        # print('GeneralAgent.init.agent_type: {}'.format(self.agent_type))
        super(GeneralAgent, self).__init__(*args, **kwargs)

    def age(self):
        return self.model.model_time - self.model_time_created

    def step(self):
        super().step()

        # print('AGENT: {}'.format(self.agent_type))
        agent_class = self.agent_type_attributes['char_class']
        # print('agent_class: {}'.format(agent_class))
        # print()
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)

        if agent_class == 'plants':
            growth_period = self.agent_type_attributes['char_growth_period']
            if self['age'] >= growth_period:
                storages = self.model.get_agents(agent_type=StorageAgent)
                selected_storages = []
                currency = 'food_edbl'
                source_value = 'char_mass_edible'
                for storage in storages:
                    if currency in storage:
                        selected_storages.append(storage)
                num_of_storages = len(selected_storages)
                for storage in selected_storages:
                    storage_value = storage[currency]
                    storage_unit = storage.agent_type_descriptions['char_capacity_' + currency]
                    agent_unit = self.agent_type_descriptions[source_value]
                    agent_value = self.agent_type_attributes[source_value]
                    step_value = pq.Quantity(agent_value, agent_unit) / num_of_storages
                    step_value.units = storage_unit
                    new_storage_value = pq.Quantity(storage_value, storage_unit) + step_value
                    storage[currency] = new_storage_value.magnitude.tolist()
                    # print('Produced {} {} of food'.format(step_value.magnitude.tolist(), storage_unit))
                self['age'] = 0

        storages = self.model.get_agents(agent_type=StorageAgent)
        for attr in self.agent_type_attributes:
            multiplier = 1
            prefix, currency = attr.split('_', 1)

            if prefix not in ['in', 'out']:
                continue

            # print('currency: {}'.format(currency))
            # print('prefix: {}'.format(prefix))

            selected_storages = []
            for storage in storages:
                if currency in storage:
                    selected_storages.append(storage)
            num_of_storages = len(selected_storages)

            if num_of_storages == 0:
                # print('Fail to find any storage for a currency: {}'.format(currency))
                # print()
                continue

            # print('num_of_storages: {}'.format(num_of_storages))

            for storage in selected_storages:
                # print('STORAGE: {}'.format(storage.agent_type))
                storage_cap = storage['char_capacity_' + currency]
                storage_unit = storage.agent_type_descriptions['char_capacity_' + currency]
                # print('\tstorage_unit: {}'.format(storage_unit))
                storage_value = pq.Quantity(storage[currency], storage_unit)
                agent_unit, agent_flow_time, attr_daytime_period = self.agent_type_descriptions[attr].split('/')
                attr_value = self.agent_type_attributes[attr]
                # print('\tattr_value: {:.4f}'.format(attr_value))
                if attr_daytime_period != '':
                    attr_daytime_period = 24 if attr_daytime_period is None else attr_daytime_period
                    # print('\tattr_daytime_period: {}'.format(attr_daytime_period))
                    multiplier *= int(attr_daytime_period) / 24
                    # print('\tmultiplier: {:.4f}'.format(multiplier))
                # print('\thours_per_step: {}'.format(hours_per_step))
                # print('\tagent_flow_rate: {} per {}'.format(agent_unit, agent_flow_time))
                if agent_flow_time == 'min':
                    multiplier *= (hours_per_step * 60)
                elif agent_flow_time == 'hour':
                    multiplier *= hours_per_step
                elif agent_flow_time == 'day':
                    multiplier *= hours_per_step / 24
                else:
                    raise Exception('Unknown agent flow_rate.time value.')
                # print('\tmultiplier: {:.4f}'.format(multiplier))
                # print('\tnum_of_storages: {}'.format(num_of_storages))
                step_value = (pq.Quantity(attr_value, agent_unit) * multiplier) / num_of_storages
                step_value.units = storage_unit
                # print('\tstep_value: {:.8f}'.format(step_value))
                if prefix == 'out':
                    new_storage_value = storage_value + step_value
                elif prefix == 'in':
                    new_storage_value = storage_value - step_value
                else:
                    raise Exception('Unknown flow type. Neither Input nor Output.')
                new_storage_value = new_storage_value.magnitude.tolist()
                if new_storage_value < 0:
                    print('\tThere is no enough {} for {}. Killing the agent'.format(currency, self.agent_type))
                    self.kill('No enough {}'.format(currency))
                elif new_storage_value > storage_cap:
                    storage[currency] = storage_cap
                    # print('\tThere is no capacity for {} in {}.'.format(currency, storage.agent_type))
                else:
                    # print('\told_storage_value: {:.8f}'.format(storage[currency]))
                    storage[currency] = new_storage_value
                    # print('\tnew_storage_value: {:.8f}'.format(storage[currency]))
                # print()
        # print()

    def kill(self, reason):
        self.destroy(reason)


class StorageAgent(EnclosedAgent):

    def __init__(self, *args, **kwargs):
        self.agent_type = kwargs.get("agent_type", None)
        # print('StorageAgent.init.agent_type: {}'.format(self.agent_type))
        super(StorageAgent, self).__init__(*args, **kwargs)

        for attr in self.agent_type_attributes:
            if attr.startswith('char_capacity'):
                attr_value = self.agent_type_attributes[attr]
                self._attr(attr, attr_value, is_client_attr=True, is_persisted_attr=True)
                currency = attr.split('_', 2)[2]
                self._attr(currency, attr_value / 2, is_client_attr=True, is_persisted_attr=True)

    def age(self):
        return self.model.model_time - self.model_time_created

    def step(self):
        super().step()

    def kill(self, reason):
        self.destroy(reason)
