r"""Describes Core Agent Types.
"""

import json
import random
from abc import ABCMeta

import numpy as np
import quantities as pq
from mesa import Agent

from simoc_server import app, db
from simoc_server.agent_model.attribute_meta import AttributeHolder
from simoc_server.database.db_model import AgentType, AgentState, CurrencyType
from simoc_server.util import load_db_attributes_into_dict
from simoc_server.util import timedelta_to_hours
from simoc_server.agent_model.agents import growth_func


class BaseAgent(Agent, AttributeHolder, metaclass=ABCMeta):
    """TODO

    TODO

    Attributes:
          agent_type_id: TODO
          active: TODO
          agent_class: TODO
          agent_type: TODO
          attrs: TODO
          attr_details: TODO
          model_time_created: TODO
          unique_id: TODO
    """

    def __init__(self, *args, **kwargs):
        """Creates a Base Agent object.

        TODO

        Args:
          agent_type: Dict, TODO
          model: Dict, TODO
        """
        self.model = kwargs.pop("model", None)
        assert self.model

        self.agent_type = kwargs.get("agent_type", None)
        self.active = kwargs.pop("active", True)
        self.model_time_created = kwargs.pop("model_time_created", self.model.time)
        self.unique_id = kwargs.pop("unique_id", None)
        if not self.unique_id:
            self.unique_id = random.getrandbits(63)

        self._load_agent_type_attributes()
        AttributeHolder.__init__(self)
        super().__init__(self.unique_id, self.model)

    def _load_agent_type_attributes(self):
        """ TODO

        Load the agent type attributes from database into class. These agent type attributes should
            be static values that define the behaviors of a particular *class* of agents. They do
            not define instance level behavoirs or traits.
        """
        agent_type = AgentType.query.filter_by(name=self.agent_type).first()
        self.agent_class = agent_type.agent_class
        self.agent_type_id = agent_type.id
        attributes, details = {}, {}
        load_db_attributes_into_dict(agent_type.agent_type_attributes, attributes, details)
        self.attrs, self.attr_details = attributes, details

    def get_agent_type(self):
        """Returns the AgentType related to the instance Agent"""
        return AgentType.query.get(self.agent_type_id)

    def get_agent_type_attribute(self, name):
        """Get agent type attribute by name as it was defined in database.

        Args:
          name: str, The name of the attribute to return.

        Returns:
          The value of the agent attribute with the given name
        """
        return self.attrs[name]

    def snapshot(self, agent_model_state):
        """TODO

        TODO

        Args:
          agent_model_state: TODO
        """
        args = dict(agent_model_state=agent_model_state,
                    agent_type_id=self.agent_type_id,
                    agent_unique_id=self.unique_id,
                    model_time_created=self.model_time_created,
                    agent_id=self.__dict__.get('id', None),
                    active=self.__dict__.get('active', None),
                    age=self.__dict__.get('age', None),
                    amount=self.__dict__.get('amount', None),
                    lifetime=self.__dict__.get('lifetime', None),
                    connections=json.dumps(self.__dict__.get('connections', None)),
                    buffer=json.dumps(self.__dict__.get('buffer', None)),
                    deprive=json.dumps(self.__dict__.get('deprive', None)))
        args['attributes'] = []
        for k in self.attribute_descriptors:
            args['attributes'].append({'name': k, 'value': self[k]})
        args['attributes'] = json.dumps(args['attributes'])
        try:
            agent_state = AgentState(**args)
            db.session.add(agent_state)
            db.session.commit()
        except:
            app.logger.exception('Failed to save a game.')
            db.session.rollback()
        finally:
            db.session.close()

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
        self.age = kwargs.pop("age", 0)
        super(EnclosedAgent, self).__init__(*args, **kwargs)
        self.full_amount = kwargs.pop("amount", 1)
        self.amount = self.full_amount
        if 'char_lifetime' in self.attrs:
            lifetime = self.attrs['char_lifetime']
            self.lifetime_units = self.attr_details['char_lifetime']['units']
            if self.lifetime_units == 'day':
                self.lifetime = int(lifetime) * self.model.day_length_hours
            elif self.lifetime_units == 'hour':
                self.lifetime = int(lifetime)
            elif self.lifetime_units == 'min':
                self.lifetime = int(lifetime / 60)
            else:
                raise Exception('Unknown agent lifetime units.')
        else:
            self.lifetime = 0
        if 'char_reproduce' in self.attrs:
            self.reproduce = self.attrs['char_reproduce']
        else:
            self.reproduce = 0
        self.growth_criteria = self.attrs.get('char_growth_criteria', None)
        self.total_growth = 0
        self.current_growth = 0
        self.growth_rate = 0
        self.grown = False
        self.agent_step_num = 0

    def step(self):
        """TODO"""
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        self.age += hours_per_step
        if not self.growth_criteria:
            self.agent_step_num = int(self.age)
        if self.grown:
            if self.reproduce:
                self.age = 0
                self.current_growth = 0
                self.growth_rate = 0
                self.agent_step_num = 0
                self.grown = False
                self.amount = self.full_amount
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
          selected_storage: TODO
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
        self.connections = kwargs.pop("connections", [])
        self.buffer = kwargs.pop("buffer", {})
        self.deprive = kwargs.pop("deprive", None)
        super(GeneralAgent, self).__init__(*args, **kwargs)
        self._init_selected_storage()
        self._calculate_step_values()
        if not self.deprive:
            self._init_deprive()

    def _init_deprive(self):
        self.deprive = {}
        for attr in self.attrs:
            prefix, currency = attr.split('_', 1)
            if prefix not in ['in', 'out']:
                continue
            deprive_value = self.attr_details[attr]['deprive_value'] or 0.0
            self.deprive[currency] = deprive_value * self.amount

    def _init_selected_storage(self):
        storages = self.model.get_agents_by_class(agent_class=StorageAgent)
        self.selected_storage = {"in": {}, 'out': {}}
        self.currency_dict = {}
        for attr in self.attrs:
            prefix, currency = attr.split('_', 1)
            if prefix not in ['in', 'out']:
                continue
            self.selected_storage[prefix][currency] = []
            self.currency_dict[currency] = CurrencyType.query.filter_by(name=currency).first()
            for storage in storages:
                if len(self.connections) > 0:
                    if storage.agent_type not in self.connections:
                        continue
                    if storage.id not in self.connections[storage.agent_type]:
                        continue
                if currency in storage:
                    self.selected_storage[prefix][currency].append(storage)

    def _calculate_step_values(self):
        if self.lifetime > 0:
            if self.lifetime_units == 'day':
                num_values = int(self.lifetime * self.model.day_length_hours)
            elif self.lifetime_units == 'hour':
                num_values = int(self.lifetime)
            elif self.lifetime_units == 'min':
                num_values = int(self.lifetime / 60)
            else:
                num_values = int(self.model.day_length_hours)
        else:
            num_values = int(self.model.day_length_hours)
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        self.step_values = {}
        for attr in self.attrs:
            prefix, currency = attr.split('_', 1)
            if prefix not in ['in', 'out']:
                continue

            agent_flow_time = self.attr_details[attr]['flow_time']
            lifetime_growth_type = self.attr_details[attr]['lifetime_growth_type']
            lifetime_growth_center = self.attr_details[attr]['lifetime_growth_center']
            lifetime_growth_min_value = self.attr_details[attr]['lifetime_growth_min_value']
            daily_growth_type = self.attr_details[attr]['daily_growth_type']
            daily_growth_center = self.attr_details[attr]['daily_growth_center']
            daily_growth_min_value = self.attr_details[attr]['daily_growth_min_value']
            lifetime_growth_min_threshold = self.attr_details[attr]['lifetime_growth_min_threshold']
            lifetime_growth_max_threshold = self.attr_details[attr]['lifetime_growth_max_threshold']
            daily_growth_min_threshold = self.attr_details[attr]['daily_growth_min_threshold']
            daily_growth_max_threshold = self.attr_details[attr]['daily_growth_max_threshold']
            daily_growth_invert = self.attr_details[attr]['daily_growth_invert']
            lifetime_growth_invert = self.attr_details[attr]['lifetime_growth_invert']
            daily_growth_noise = self.attr_details[attr]['daily_growth_noise']
            lifetime_growth_noise = self.attr_details[attr]['lifetime_growth_noise']
            daily_growth_scale = self.attr_details[attr]['daily_growth_scale']
            lifetime_growth_scale = self.attr_details[attr]['lifetime_growth_scale']
            daily_growth_steepness = self.attr_details[attr]['daily_growth_steepness']
            lifetime_growth_steepness = self.attr_details[attr]['lifetime_growth_steepness']

            multiplier = 1
            if agent_flow_time == 'min':
                multiplier *= (hours_per_step * 60)
            elif agent_flow_time == 'hour':
                multiplier *= hours_per_step
            elif agent_flow_time == 'day':
                multiplier *= hours_per_step / self.model.day_length_hours
            else:
                raise Exception('Unknown agent flow_rate.time value.')
            agent_value = float(self.attrs[attr])
            agent_value *= float(multiplier)

            if lifetime_growth_type:
                start_value = lifetime_growth_min_value or 0.0
                center = lifetime_growth_center or None
                min_threshold = lifetime_growth_min_threshold or 0.0
                min_threshold *= num_values
                max_threshold = lifetime_growth_max_threshold or 0.0
                max_threshold *= num_values
                invert = bool(lifetime_growth_invert)
                noise = bool(lifetime_growth_noise)
                kwargs = {'agent_value': agent_value,
                          'num_values': num_values,
                          'growth_type': lifetime_growth_type,
                          'min_value': start_value,
                          'min_threshold': int(min_threshold),
                          'max_threshold': int(max_threshold),
                          'center': center,
                          'noise': noise,
                          'invert': invert}
                if lifetime_growth_scale:
                    kwargs['scale'] = lifetime_growth_scale
                if lifetime_growth_steepness:
                    kwargs['steepness'] = lifetime_growth_steepness
                self.step_values[attr] = growth_func.get_growth_values(**kwargs)
            else:
                self.step_values[attr] = np.ones(num_values) * agent_value

            if daily_growth_type:
                day_length = int(self.model.day_length_hours)
                center = daily_growth_center or None
                min_threshold = daily_growth_min_threshold or 0.0
                min_threshold *= self.model.day_length_hours
                max_threshold = daily_growth_max_threshold or 0.0
                max_threshold *= self.model.day_length_hours
                invert = bool(daily_growth_invert)
                noise = bool(daily_growth_noise)
                for i in range(0, num_values, day_length):
                    day_values = self.step_values[attr][i:i+day_length]
                    agent_value = np.mean(day_values)
                    daily_min = np.min(day_values)
                    daily_max = np.max(day_values)
                    if daily_growth_min_value:
                        start_value = agent_value * daily_growth_min_value
                    elif daily_min < daily_max:
                        start_value = daily_min or 0
                    else:
                        start_value = 0
                    if (i + day_length) > num_values:
                        day_length = num_values - i
                    kwargs = {'agent_value': agent_value,
                              'num_values': day_length,
                              'growth_type': daily_growth_type,
                              'min_value': start_value,
                              'min_threshold': int(min_threshold),
                              'max_threshold': int(max_threshold),
                              'center': center,
                              'noise': noise,
                              'invert': invert}
                    if daily_growth_scale:
                        kwargs['scale'] = daily_growth_scale
                    if daily_growth_steepness:
                        kwargs['steepness'] = daily_growth_steepness
                    if start_value == agent_value:
                        self.step_values[attr][i:i+day_length] = np.ones(day_length) * agent_value
                    else:
                        self.step_values[attr][i:i+day_length] = growth_func.get_growth_values(**kwargs)

            if attr == self.growth_criteria:
                self.total_growth = np.sum(self.step_values[attr])

    def get_step_value(self, attr):
        """TODO

        TODO

        Args:
            attr: TODO

        Returns:
          TODO
        """
        prefix, currency = attr.split('_', 1)
        agent_unit = self.attr_details[attr]['flow_unit']
        cr_name = self.attr_details[attr]['criteria_name']
        cr_limit = self.attr_details[attr]['criteria_limit']
        cr_value = self.attr_details[attr]['criteria_value'] or 0.0
        cr_buffer = self.attr_details[attr]['criteria_buffer'] or 0.0
        weighted = self.attr_details[attr]['weighted']
        # Only apply weighted actions when grown
        if self.grown and not weighted:
            return pq.Quantity(0.0, agent_unit)
        # Ignore growth_rate criteria when grown and weighted
        if cr_name == "growth_rate" and self.grown and weighted:
            pass
        elif cr_name:
            if cr_name in self:
                source = self[cr_name]
            else:
                source = 0
                for storage_id in self.model.storage_ratios:
                    if cr_name in self.model.storage_ratios[storage_id]:
                        source += self.model.storage_ratios[storage_id][cr_name]
            cr_id = '{}_{}_{}'.format(prefix, currency, cr_name)
            if cr_limit == '>':
                if source < cr_value:
                    if self.buffer.get(cr_id, 0) > 0:
                        self.buffer[cr_id] -= 1
                    else:
                        return pq.Quantity(0.0, agent_unit)
                elif cr_buffer > 0:
                    self.buffer[cr_id] = cr_buffer
            elif cr_limit == '<':
                if source > cr_value:
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
        step_num = int(self.agent_step_num)
        if step_num >= self.step_values[attr].shape[0]:
            step_num = step_num % int(self.model.day_length_hours)
        agent_value = self.step_values[attr][step_num]
        if weighted and weighted in self:
            agent_value *= self[weighted]
        return pq.Quantity(agent_value, agent_unit)

    def step(self, value_eps=1e-12, value_round=6):
        """TODO

        TODO

        Raises:
        Exception: TODO
        """
        super().step()
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        if self.age + hours_per_step >= self.lifetime > 0:
            self.grown = True
        for attr in self.attrs:
            if attr.startswith('char_threshold_'):
                threshold_value = self.attrs[attr]
                threshold_type = attr.split('_', 3)[2]
                currency = attr.split('_', 3)[3]
                for prefix in ['in', 'out']:
                    if currency in self.selected_storage[prefix]:
                        for storage in self.selected_storage[prefix][currency]:
                            agent_id = '{}_{}'.format(storage.agent_type, storage.id)
                            if threshold_type == 'lower' and self.model.storage_ratios[agent_id][
                                currency + '_ratio'] < threshold_value:
                                self.kill('Threshold {} met for {}. Killing the agent'.format(
                                    currency, self.agent_type))
                                return
                            if threshold_type == 'upper' and self.model.storage_ratios[agent_id][
                                currency + '_ratio'] > threshold_value:
                                self.kill('Threshold {} met for {}. Killing the agent'.format(
                                    currency, self.agent_type))
                                return
        influx = set()
        skip_step = False
        for prefix in ['in', 'out']:
            for currency in self.selected_storage[prefix]:
                attr = '{}_{}'.format(prefix, currency)
                num_of_storages = len(self.selected_storage[prefix][currency])
                if num_of_storages == 0:
                    self.kill('No storage of {} found for {}. Killing the agent'.format(
                        currency, self.agent_type))
                deprive_unit = self.attr_details[attr]['deprive_unit']
                deprive_value = self.attr_details[attr]['deprive_value'] or 0.0
                if deprive_value > 0:
                    if deprive_unit == 'min':
                        delta_per_step = hours_per_step * 60
                    elif deprive_unit == 'hour':
                        delta_per_step = hours_per_step
                    elif deprive_unit == 'day':
                        delta_per_step = hours_per_step / int(self.model.day_length_hours)
                    else:
                        raise Exception('Unknown agent deprive_unit value.')
                else:
                    delta_per_step = 0
                is_required = self.attr_details[attr]['is_required'] or ''
                requires = self.attr_details[attr]['requires'] or []
                if len(requires) > 0 and len(set(requires).difference(influx)) > 0:
                    continue
                step_value = self.get_step_value(attr) / num_of_storages
                for storage in self.selected_storage[prefix][currency]:
                    value = agent_amount = 0
                    for i in range(self.amount, 0, -1):
                        storage_cap = storage['char_capacity_' + currency]
                        attr_name = 'char_capacity_' + currency
                        storage_unit = storage.attr_details[attr_name]['units']
                        storage_value = pq.Quantity(storage[currency], storage_unit)
                        step_value.units = storage_unit
                        if prefix == 'in':
                            new_storage_value = storage_value - step_value * i
                        elif prefix == 'out':
                            new_storage_value = storage_value + step_value * i
                        else:
                            raise Exception('Unknown flow type. Neither Input nor Output.')
                        new_storage_value = new_storage_value.magnitude.tolist()
                        if new_storage_value < 0 <= storage_value:
                            if deprive_value > 0:
                                self.deprive[currency] -= delta_per_step
                                if self.deprive[currency] < 0:
                                    self.amount -= 1
                                if self.amount <= 0:
                                    self.kill(f'All {self.agent_type} are died. Killing the agent')
                                    return
                            if is_required == 'mandatory':
                                return
                            elif is_required == 'desired':
                                skip_step = True
                        else:
                            if not skip_step or is_required or self.attr_details[attr]['criteria_name']:
                                storage[currency] = min(new_storage_value, storage_cap)
                                if deprive_value > 0:
                                    self.deprive[currency] = min(deprive_value * self.amount,
                                                                 self.deprive[currency] +
                                                                 deprive_value)
                                agent_amount = i
                                value = float(step_value.magnitude.tolist()) * i
                                if attr == self.growth_criteria:
                                    self.agent_step_num += hours_per_step
                            break
                    if value > value_eps:
                        if prefix == 'in' and currency not in influx:
                            influx.add(currency)
                        currency_type = self.currency_dict[currency]
                        if attr == self.growth_criteria:
                            self.current_growth += (value / agent_amount)
                            self.growth_rate = self.current_growth / self.total_growth
                            growth = self.growth_rate
                        else:
                            growth = None
                        record = {"step_num": self.model.step_num + 1,
                                  'game_id': self.model.game_id,
                                  "user_id": self.model.user_id,
                                  "agent_type": self.agent_type,
                                  "agent_type_id": self.agent_type_id,
                                  "agent_id": self.unique_id,
                                  "direction": prefix,
                                  "agent_amount": agent_amount,
                                  "currency_type": currency_type.name,
                                  "currency_type_id": currency_type.id,
                                  "value": round(value, value_round),
                                  "growth": growth,
                                  "unit": str(step_value.units),
                                  "storage_type": storage.agent_type,
                                  "storage_type_id": storage.agent_type_id,
                                  "storage_agent_id": storage.unique_id,
                                  "storage_id": storage.id}
                        self.model.step_records_buffer.append(record)

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
        self.id = kwargs.pop("id", None)
        super(StorageAgent, self).__init__(*args, **kwargs)
        for attr in self.attrs:
            if attr.startswith('char_capacity'):
                currency = attr.split('_', 2)[2]
                initial_value = kwargs.get(currency, None)
                initial_value = initial_value if initial_value is not None else 0
                self._attr(currency, initial_value, is_client_attr=True, is_persisted_attr=True)
                capacity = self.attrs[attr]
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
