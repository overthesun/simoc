from abc import ABCMeta, abstractmethod
from mesa import Agent
from uuid import uuid4
import inspect

from simoc_server import db
from simoc_server.util import load_db_attributes_into_dict, NotLoaded
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


    def __init__(self, *args, **kwargs):
        self.agent_type = kwargs.get("agent_type", None)
        agent_state = kwargs.get("agent_state", None)
        model = kwargs.get("model", None)
        self._load_agent_type_attributes()
        AttributeHolder.__init__(self)

        self.active = True
        if agent_state is not None:
            self.load_from_db(agent_state)
            super().__init__(self.unique_id, model)
        else:
            self.unique_id = "{0}_{1}".format(self.__class__.__name__, uuid4())
            self.model_time_created = model['time']
            super().__init__(self.unique_id, model)

        self._attr('age', 0, is_client_attr=True, is_persisted_attr=True)

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
        if self.agent_type is None:
            raise Exception("agent_type not set for class {}".format(self))

        if self._last_loaded_type_attr_class is not self:
            agent_type_name = self.agent_type
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
        return AgentType.query.get(self._agent_type_id)

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
        agent_state = AgentState(agent_type_id=self._agent_type_id,
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
        super(EnclosedAgent, self).__init__(*args, **kwargs)

    def step(self):
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        self['age'] += hours_per_step / 24
        if 'char_lifetime' in self.agent_type_attributes:
            lifetime = self.agent_type_attributes['char_lifetime']
            if self['age'] >= lifetime:
                if 'char_reproduce' in self.agent_type_attributes:
                    reproduce = self.agent_type_attributes['char_lifetime']
                    if reproduce:
                        self['age'] = 0
                        return
                self.destroy('Lifetime limit has been reached by {}. Killing the agent'.format(self.agent_type))

    def destroy(self, reason):
        self.model.logger.info("Object Died! Reason: {}".format(reason))
        print("Object Died! Reason: {}".format(reason))
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
        connections = kwargs.pop("connections", None)

        super(GeneralAgent, self).__init__(*args, **kwargs)

        self.buffer = {}

        storages = self.model.get_agents_by_class(agent_class=StorageAgent)
        self.selected_storages = {"in": {}, 'out': {}}
        self.deprive = {}
        for attr in self.agent_type_attributes:
            prefix, currency = attr.split('_', 1)
            if prefix not in ['in', 'out']:
                continue

            descriptions = self.agent_type_descriptions[attr].split('/')
            deprive_value = descriptions[8]
            required = descriptions[9]
            # Iurii: Can we alter this to accept floats
            self.deprive[currency] = int(deprive_value) if deprive_value != '' else 0

            self.selected_storages[prefix][currency] = []
            for storage in storages:
                if len(connections) > 0:
                    if storage.agent_type not in connections:
                        continue
                    if storage.id not in connections[storage.agent_type]:
                        continue
                if currency in storage:
                    self.selected_storages[prefix][currency].append(storage)

    def age(self):
        return self.model['time'] - self.model_time_created

    def get_step_value(self, attr, hours_per_step):
        prefix, currency = attr.split('_', 1)
        multiplier = 1
        descriptions = self.agent_type_descriptions[attr].split('/')
        agent_unit, agent_flow_time, attr_active_period = descriptions[:3]
        if attr_active_period != '':
            multiplier *= int(attr_active_period) / 24
        cr_name, cr_limit, cr_value, cr_buffer = descriptions[3:7]
        cr_value = float(cr_value) if cr_value != '' else 0.0
        cr_buffer = int(cr_buffer) if cr_buffer != '' else 0
        if len(cr_name) > 0:
            if cr_name in self:
                source = self[cr_name]
            else:
                source = 0                                
                for curr in self.selected_storages[prefix]:
                    for storage in self.selected_storages[prefix][curr]:
                        agent_id = '{}_{}'.format(storage.agent_type, storage.id)                           
                        if cr_name in self.model.model_stats[agent_id]:
                            source += self.model.model_stats[agent_id][cr_name]
            cr_id = '{}_{}_{}'.format(prefix, currency, cr_name)
            #Test line
            #print(str(self.agent_type)+" Source: " +str(source)+ " Limit: " + str(cr_value))
            if cr_limit == '>':
                if source <= cr_value:
                    if self.buffer.get(cr_id, 0) > 0:
                        self.buffer[cr_id] -= 1
                    else:
                        return pq.Quantity(0.0, agent_unit)
                elif cr_buffer > 0:
                    self.buffer[cr_id] = cr_buffer
            elif cr_limit == '<':
                if source >= cr_value:
                    if self.buffer.get(cr_id, 0) > 0:
                        self.buffer[cr_id] -= 1
                    else:
                        return pq.Quantity(0.0, agent_unit)
                elif cr_buffer > 0:
                    self.buffer[cr_id] = cr_buffer
            elif cr_limit == '=':
                if cr_value != source:
                    if self.buffer.get(cr_id, 0) > 0:
                        self.buffer[cr_id] -= 1
                    else:
                        return pq.Quantity(0.0, agent_unit)
                elif cr_buffer > 0:
                    self.buffer[cr_id] = cr_buffer
        if agent_flow_time == 'min':
            multiplier *= (hours_per_step * 60)
        elif agent_flow_time == 'hour':
            multiplier *= hours_per_step
        elif agent_flow_time == 'day':
            multiplier *= hours_per_step / 24
        else:
            raise Exception('Unknown agent flow_rate.time value.')
        agent_value = pq.Quantity(self.agent_type_attributes[attr], agent_unit)
        return agent_value * float(multiplier)


    def step(self):
        super().step()
        on = False

        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)

        for attr in self.agent_type_attributes:
            if attr.startswith('char_threshold_'):
                threshold_value = self.agent_type_attributes[attr]
                currency = attr.split('_', 2)[2]
                for prefix in ['in', 'out']:
                    if currency in self.selected_storages[prefix]:
                        for storage in self.selected_storages[prefix][currency]:
                            agent_id = '{}_{}'.format(storage.agent_type, storage.id)
                            if self.model.model_stats[agent_id][currency + '_ratio'] < threshold_value:
                                self.kill('Threshold {} met for {}. Killing the agent'.format(currency, self.agent_type))

        influx = []
        for prefix in ['in', 'out']:
            for currency in self.selected_storages[prefix]:
                attr = '{}_{}'.format(prefix, currency)
                num_of_storages = len(self.selected_storages[prefix][currency])
                if num_of_storages == 0:
                    self.kill('No storage of {} found for {}. Killing the agent'.format(currency, self.agent_type))
                descriptions = self.agent_type_descriptions[attr].split('/')
                deprive_unit, deprive_value = descriptions[7:9]
                required, requires = descriptions[9:11]
                if requires != 'None':
                    requires = requires.split('#')
                    for req_currency in requires:
                        if req_currency not in influx:
                            continue
                # Iurii: Can we change this to accept floats?
                deprive_value = int(deprive_value) if deprive_value != '' else 0
                step_value = self.get_step_value(attr, hours_per_step) / num_of_storages
                for storage in self.selected_storages[prefix][currency]:
                    storage_cap = storage['char_capacity_' + currency]
                    storage_unit = storage.agent_type_descriptions['char_capacity_' + currency]
                    storage_value = pq.Quantity(storage[currency], storage_unit)
                    step_value.units = storage_unit
                    if prefix == 'out':
                        new_storage_value = storage_value + step_value
                    elif prefix == 'in':
                        new_storage_value = storage_value - step_value
                    else:
                        raise Exception('Unknown flow type. Neither Input nor Output.')
                    new_storage_value = new_storage_value.magnitude.tolist()
                    if new_storage_value < 0 and storage_value >= 0:
                        if deprive_value > 0:
                            if deprive_unit == 'min':
                                delta_per_step = hours_per_step * 60
                            elif deprive_unit == 'hour':
                                delta_per_step = hours_per_step
                            elif deprive_unit == 'day':
                                delta_per_step = hours_per_step / 24
                            else:
                                raise Exception('Unknown agent deprive_unit value.')
                            self.deprive[currency] -= delta_per_step
                            if self.deprive[currency] < 0:
                                self.kill(
                                    'There is no enough {} for {}. Killing the agent'.format(currency, self.agent_type))
                        if required == 'True':
                            return
                        else:
                            storage[currency] = 0
                    else:
                        storage[currency] = min(new_storage_value, storage_cap)
                        if prefix == 'in':
                            influx.append(currency)
                        if deprive_value > 0:
                            self.deprive[currency] = deprive_value

    def kill(self, reason):
        self.destroy(reason)


class StorageAgent(EnclosedAgent):

    def __init__(self, *args, **kwargs):
        self.agent_type = kwargs.get("agent_type", None)
        self.id = kwargs.get("id", None)
        super(StorageAgent, self).__init__(*args, **kwargs)

        for attr in self.agent_type_attributes:
            if attr.startswith('char_capacity'):
                currency = attr.split('_', 2)[2]
                initial_value = kwargs.get(currency, None)
                initial_value = initial_value if initial_value is not None else 0
                self._attr(currency, initial_value, is_client_attr=True, is_persisted_attr=True)
                capacity = self.agent_type_attributes[attr]
                self._attr(attr, capacity, is_client_attr=True, is_persisted_attr=True)

    def age(self):
        return self.model['time'] - self.model_time_created

    def step(self):
        super().step()

    def kill(self, reason):
        self.destroy(reason)
