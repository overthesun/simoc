r"""Describes Core Agent Types.
"""

import json
from abc import ABCMeta
from uuid import uuid4

import numpy as np
import quantities as pq
from mesa import Agent

from simoc_server import db
from simoc_server.agent_model.attribute_meta import AttributeHolder
from simoc_server.database.db_model import AgentType, AgentState
from simoc_server.util import load_db_attributes_into_dict
from simoc_server.util import timedelta_to_hours
from simoc_server.agent_model.agents import growth_func


class BaseAgent(Agent, AttributeHolder, metaclass=ABCMeta):
    """TODO

    TODO

    Attributes:
          _agent_type_id: TODO
          _last_loaded_type_attr_class: TODO
          active: TODO
          agent_class: TODO
          agent_type: TODO
          agent_type_attributes: TODO
          agent_type_descriptions: TODO
          model_time_created: TODO
          unique_id: TODO
    """

    # Used to ensure type attributes are properly inherited and only loaded once
    _last_loaded_type_attr_class = False

    def __init__(self, *args, **kwargs):
        """Creates a Base Agent object.

        TODO

        Args:
          agent_type: Dict, TODO
          model: Dict, TODO
        """
        self._load_agent_type_attributes()
        AttributeHolder.__init__(self)
        self.active = True
        self.unique_id = "{0}_{1}".format(self.__class__.__name__, uuid4().hex[:8])
        self.agent_type = kwargs.get("agent_type", None)
        model = kwargs.get("model", None)
        self.model_time_created = model.time
        super().__init__(self.unique_id, model)

    def _load_agent_type_attributes(self):
        """ TODO

        Load the agent type attributes from database into class. These agent type attributes should
            be static values that define the behaviors of a particular *class* of agents. They do
            not define instance level behavoirs or traits.

        Raises:
            Exception: if class does not define _agent_type_name or if the specified agent type
            cannot be located in the database
        """
        if self.agent_type is None:
            raise Exception("agent_type not set for class {}".format(self))

        if self._last_loaded_type_attr_class is not self:
            agent_type_name = self.agent_type
            agent_type = AgentType.query.filter_by(
                name=agent_type_name).first()
            self.agent_class = agent_type.agent_class

            if agent_type is None:
                raise Exception(
                    "Cannot find agent_type in database with name '{0}'. Please"
                    " create associated AgentType and add to database".format(
                        agent_type_name))

            attributes, descriptions = {}, {}
            try:
                load_db_attributes_into_dict(
                    agent_type.agent_type_attributes, attributes, descriptions)
            except ValueError as e:
                raise ValueError(
                    "Error loading agent type attributes for class '{}'.".format(
                        self.__name__)) from e

            self.agent_type_attributes, self.agent_type_descriptions = attributes, descriptions

            self._last_loaded_type_attr_class = self

            # store agent type id for later saving of agent state
            self._agent_type_id = agent_type.id

    def get_agent_type(self):
        """Returns the AgentType related to the instance Agent"""
        return AgentType.query.get(self._agent_type_id)

    def get_agent_type_attribute(self, name):
        """Get agent type attribute by name as it was defined in database.

        Args:
          name: str, The name of the attribute to return.

        Returns:
          The value of the agent attribute with the given name
        """
        return self.agent_type_attributes[name]

    def snapshot(self, agent_model_state, commit=True):
        """TODO

        TODO

        Args:
          agent_model_state: TODO
          commit: bool, TODO
        """
        args = dict(agent_type_id=self._agent_type_id,
                    agent_model_state=agent_model_state,
                    agent_unique_id=self.unique_id,
                    model_time_created=self.model_time_created,
                    active=self.active,
                    age=self.age,
                    agent_id=self.__dict__.get('id', None),
                    lifetime=self.lifetime,
                    agent_type_attributes=json.dumps(self.agent_type_attributes),
                    agent_type_descriptions=json.dumps(self.agent_type_descriptions),
                    buffer=json.dumps(self.__dict__.get('buffer', None)),
                    deprive=json.dumps(self.__dict__.get('deprive', None)))
        args['attribute_descriptors'] = []
        attribute_descriptors = self.attribute_descriptors
        for k in attribute_descriptors:
            args['attribute_descriptors'].append(
                [k, attribute_descriptors[k]._type.__name__,
                 attribute_descriptors[k].is_client_attr,
                 attribute_descriptors[k].is_persisted_attr])
        args['attribute_descriptors'] = json.dumps(args['attribute_descriptors'])
        args['storage'] = {}
        for attr in self.agent_type_attributes:
            if attr.startswith('char_capacity'):
                currency = attr.split('_', 2)[2]
                args['storage'][currency] = self[currency]
        args['storage'] = json.dumps(args['storage'])
        args['selected_storages'] = []
        selected_storages = self.__dict__.get('selected_storages', [])
        for k in selected_storages:
            for v in selected_storages[k]:
                for storage in selected_storages[k][v]:
                    args['selected_storages'].append(
                        [k, v, storage.agent_type, storage.id, storage.unique_id])
        args['selected_storages'] = json.dumps(args['selected_storages'])
        agent_state = AgentState(**args)

        db.session.add(agent_state)
        if commit:
            db.session.commit()

    def destroy(self):
        """Destroys the agent and removes it from the model"""
        self.active = False
        self.model.remove(self)


class EnclosedAgent(BaseAgent):
    """TODO

    TODO

    Attributes:
          age: TODO
          agent_type: TODO
          cause_of_death: TODO
          lifetime: TODO
    """

    def __init__(self, *args, **kwargs):
        """Creates an Enclosed Agent object.

        TODO

        Args:
          agent_type: TODO
        """
        self.age = 0
        self.agent_type = kwargs.get("agent_type", None)
        super(EnclosedAgent, self).__init__(*args, **kwargs)
        if 'char_lifetime' in self.agent_type_attributes:
            self.lifetime = self.agent_type_attributes['char_lifetime']
        else:
            self.lifetime = 0
        if 'char_reproduce' in self.agent_type_attributes:
            self.reproduce = self.agent_type_attributes['char_reproduce']
        else:
            self.reproduce = 0

    def step(self):
        """TODO"""
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        self.age += hours_per_step / self.model.day_length_hours
        if 0 < self.lifetime <= self.age:
            if self.reproduce:
                self.age = 0
                return
            self.destroy('Lifetime limit has been reached by {}. Killing the agent'.format(
                    self.agent_type))

    def age(self):
        """Return the age of the agent."""
        return self.model.time - self.model_time_created

    def destroy(self, reason):
        """Destroys the agent and removes it from the model

        Args:
          reason: str, cause of death
        """
        self.model.logger.info("Object Died! Reason: {}".format(reason))
        print("Object Died! Reason: {}".format(reason))
        self.cause_of_death = reason
        super().destroy()


class GeneralAgent(EnclosedAgent):
    """TODO

    TODO

    Attributes:
          agent_type: TODO
          buffer: TODO
          deprive: TODO
          selected_storages: TODO
    """

    def __init__(self, *args, **kwargs):
        """Creates a General Agent object.

        TODO

        Args:
          agent_type: Dict, TODO
          connections: Dict, TODO
          model: Dict, TODO
          amount: Dict, TODO
        """
        self.agent_type = kwargs.get("agent_type", None)
        connections = kwargs.pop("connections", None)
        model = kwargs.get("model", None)
        amount = kwargs.get("amount", None)
        super(GeneralAgent, self).__init__(*args, **kwargs)
        self.buffer = {}
        self.deprive = {}
        self.step_values = {}
        num_values = int((self.lifetime or 1) * self.model.day_length_hours) + 1
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        storages = self.model.get_agents_by_class(agent_class=StorageAgent)
        self.selected_storages = {"in": {}, 'out': {}}
        for attr in self.agent_type_attributes:
            prefix, currency = attr.split('_', 1)
            if prefix not in ['in', 'out']:
                continue
            descriptions = self.agent_type_descriptions[attr].split(';')
            deprive_value = descriptions[7]
            self.deprive[currency] = int(
                deprive_value) if deprive_value != '' else 0
            if (model.single_agent == 1 and (
                    self.agent_class == "plants" or self.agent_class == "power_generation")):
                self.agent_type_attributes[attr] *= amount
            self.selected_storages[prefix][currency] = []
            for storage in storages:
                if len(connections) > 0:
                    if storage.agent_type not in connections:
                        continue
                    if storage.id not in connections[storage.agent_type]:
                        continue
                if currency in storage:
                    self.selected_storages[prefix][currency].append(storage)

            descriptions = self.agent_type_descriptions[attr].split(';')
            agent_flow_time = descriptions[1]
            lifetime_growth_type, lifetime_growth_center, lifetime_growth_min_value = descriptions[10:13]
            daily_growth_type, daily_growth_center, daily_growth_min_rate = descriptions[13:16]
            lifetime_growth_min_threshold, lifetime_growth_max_threshold = descriptions[16:18]
            daily_growth_min_threshold, daily_growth_max_threshold = descriptions[18:20]
            daily_growth_invert, lifetime_growth_invert = descriptions[20:22]
            daily_growth_noise, lifetime_growth_noise = descriptions[22:24]
            daily_growth_scale, lifetime_growth_scale = descriptions[24:26]
            daily_growth_steepness, lifetime_growth_steepness = descriptions[26:28]

            multiplier = 1
            if agent_flow_time == 'min':
                multiplier *= (hours_per_step * 60)
            elif agent_flow_time == 'hour':
                multiplier *= hours_per_step
            elif agent_flow_time == 'day':
                multiplier *= hours_per_step / self.model.day_length_hours
            else:
                raise Exception('Unknown agent flow_rate.time value.')
            agent_value = self.agent_type_attributes[attr]
            agent_value *= float(multiplier)

            if lifetime_growth_type:
                start_value = float(lifetime_growth_min_value) \
                    if len(lifetime_growth_min_value) > 0 else 0.0
                center = float(lifetime_growth_center) * self.model.day_length_hours \
                    if len(lifetime_growth_center) > 0 else None
                min_threshold = int(lifetime_growth_min_threshold) * self.model.day_length_hours \
                    if len(lifetime_growth_min_threshold) > 0 else 0
                max_threshold = int(lifetime_growth_max_threshold) * self.model.day_length_hours \
                    if len(lifetime_growth_max_threshold) > 0 else 0
                scale = float(lifetime_growth_scale) \
                    if len(lifetime_growth_scale) > 0 else None
                steepness = float(lifetime_growth_steepness) / self.model.day_length_hours \
                    if len(lifetime_growth_steepness) > 0 else None
                invert = bool(lifetime_growth_invert)
                noise = bool(lifetime_growth_noise)
                kwargs = {'agent_value': agent_value,
                          'num_values': num_values,
                          'growth_type': lifetime_growth_type,
                          'min_value': start_value,
                          'min_threshold': min_threshold,
                          'max_threshold': max_threshold,
                          'center': center,
                          'noise': noise,
                          'invert': invert,
                          'steepness': steepness,
                          'scale': scale}
                self.step_values[attr] = growth_func.get_growth_values(**kwargs)
            else:
                self.step_values[attr] = np.ones(num_values) * agent_value

            if daily_growth_type:
                day_length = int(self.model.day_length_hours)
                center = float(daily_growth_center) \
                    if len(daily_growth_center) > 0 else None
                min_threshold = int(daily_growth_min_threshold) \
                    if len(daily_growth_min_threshold) > 0 else 0
                max_threshold = int(daily_growth_max_threshold) \
                    if len(daily_growth_max_threshold) > 0 else 0
                scale = float(daily_growth_scale) \
                    if len(daily_growth_scale) > 0 else None
                steepness = float(daily_growth_steepness) \
                    if len(daily_growth_steepness) > 0 else None
                invert = bool(daily_growth_invert)
                noise = bool(daily_growth_noise)
                for i in range(0, num_values, day_length):
                    day_values = self.step_values[attr][i:i+day_length]
                    agent_value = np.mean(day_values)
                    daily_min = np.min(day_values)
                    daily_max = np.max(day_values)
                    if len(daily_growth_min_rate) > 0:
                        start_value = agent_value * float(daily_growth_min_rate)
                    elif daily_min < daily_max:
                        start_value = daily_min
                    else:
                        start_value = 0
                    if (i + day_length) > num_values:
                        day_length = num_values - i
                    kwargs = {'agent_value': agent_value,
                              'num_values': day_length,
                              'growth_type': daily_growth_type,
                              'min_value': start_value,
                              'min_threshold': min_threshold,
                              'max_threshold': max_threshold,
                              'center': center,
                              'noise': noise,
                              'invert': invert,
                              'steepness': steepness,
                              'scale': scale}
                    self.step_values[attr][i:i+day_length] = growth_func.get_growth_values(**kwargs)

    def get_step_value(self, attr):
        """TODO

        TODO

        Args:
            attr: TODO

        Returns:
          TODO
        """
        prefix, currency = attr.split('_', 1)
        descriptions = self.agent_type_descriptions[attr].split(';')
        agent_unit = descriptions[0]
        cr_name, cr_limit, cr_value, cr_buffer = descriptions[2:6]
        cr_value = float(cr_value) if cr_value != '' else 0.0
        cr_buffer = int(cr_buffer) if cr_buffer != '' else 0
        if len(cr_name) > 0:
            if cr_name in self:
                source = self[cr_name]
            else:
                source = 0
                for curr in self.selected_storages[prefix]:
                    for storage in self.selected_storages[prefix][curr]:
                        agent_id = '{}_{}'.format(
                            storage.agent_type, storage.id)
                        if cr_name in self.model.model_stats[agent_id]:
                            source += self.model.model_stats[agent_id][cr_name]
            cr_id = '{}_{}_{}'.format(prefix, currency, cr_name)
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
        step_num = int(self.age * self.model.day_length_hours)
        if step_num >= self.step_values[attr].shape[0]:
            step_num = int(step_num % self.model.day_length_hours)
        agent_value = self.step_values[attr][step_num]
        return pq.Quantity(agent_value, agent_unit)

    def step(self):
        """TODO

        TODO

        Raises:
        Exception: TODO
        """
        super().step()
        on = False
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        for attr in self.agent_type_attributes:
            if attr.startswith('char_threshold_'):
                threshold_value = self.agent_type_attributes[attr]
                type = attr.split('_', 3)[2]
                currency = attr.split('_', 3)[3]
                for prefix in ['in', 'out']:
                    if currency in self.selected_storages[prefix]:
                        for storage in self.selected_storages[prefix][currency]:
                            agent_id = '{}_{}'.format(
                                storage.agent_type, storage.id)
                            if type == 'lower' and self.model.model_stats[agent_id][
                                currency + '_ratio'] < threshold_value:
                                self.kill('Threshold {} met for {}. Killing the agent'.format(
                                    currency, self.agent_type))
                            if type == 'upper' and self.model.model_stats[agent_id][
                                currency + '_ratio'] > threshold_value:
                                self.kill('Threshold {} met for {}. Killing the agent'.format(
                                    currency, self.agent_type))
        influx = []
        for prefix in ['in', 'out']:
            for currency in self.selected_storages[prefix]:
                log = False
                attr = '{}_{}'.format(prefix, currency)
                num_of_storages = len(self.selected_storages[prefix][currency])
                if num_of_storages == 0:
                    self.kill('No storage of {} found for {}. Killing the agent'.format(
                        currency, self.agent_type))
                descriptions = self.agent_type_descriptions[attr].split(';')
                deprive_unit, deprive_value = descriptions[6:8]
                is_required, requires = descriptions[8:10]
                if requires != 'None':
                    requires = requires.split('#')
                    for req_currency in requires:
                        if req_currency not in influx:
                            continue
                deprive_value = int(deprive_value) if deprive_value != '' else 0
                step_value = self.get_step_value(attr) / num_of_storages
                for storage in self.selected_storages[prefix][currency]:
                    storage_cap = storage['char_capacity_' + currency]
                    storage_unit = storage.agent_type_descriptions[
                        'char_capacity_' + currency]
                    storage_value = pq.Quantity(
                        storage[currency], storage_unit)
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
                                delta_per_step = hours_per_step / int(self.model.day_length_hours)
                            else:
                                raise Exception('Unknown agent deprive_unit value.')
                            self.deprive[currency] -= delta_per_step
                            if self.deprive[currency] < 0:
                                self.kill('There is no enough {} for {}. Killing the agent'.format(
                                    currency, self.agent_type))
                        if is_required == 'True':
                            return
                        else:
                            log = True
                            storage[currency] = 0
                    else:
                        log = True
                        storage[currency] = min(new_storage_value, storage_cap)
                        if prefix == 'in':
                            influx.append(currency)
                        if deprive_value > 0:
                            self.deprive[currency] = deprive_value
                    if self.model.logging is not None and log:
                        record = {"step_num": self.model.step_num,
                                  "agent_type": self.agent_type,
                                  "agent_id": self.unique_id,
                                  "direction": prefix,
                                  "currency": currency,
                                  "value": step_value.magnitude.tolist(),
                                  "unit": str(step_value.units),
                                  "storage_type": storage.agent_type,
                                  "storage_id": storage.id}
                        self.model.logs.append(record)

    def kill(self, reason):
        """Destroys the agent and removes it from the model

        Args:
          reason: str, cause of death
        """
        self.destroy(reason)


class StorageAgent(EnclosedAgent):
    """TODO

    TODO

    Attributes:
          agent_type: TODO
          id: TODO
    """

    def __init__(self, *args, **kwargs):
        """Creates an Agent Initializer object.

        TODO

        Args:
          agent_type: TODO
          id: TODO
          currency: TODO
        """
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

    def step(self):
        """TODO"""
        super().step()

    def kill(self, reason):
        """Destroys the agent and removes it from the model

        Args:
          reason: str, cause of death
        """
        self.destroy(reason)
