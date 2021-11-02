r"""Describes Core Agent Types.
"""

import json
import operator
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
from simoc_server.exceptions import ServerError
from simoc_server.agent_model.agents import custom_funcs


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
        self.currency_dict = {}
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

    def add_currency_to_dict(self, currency):
        """Adds a reference to the currency's database object.

        Args:
          currency: str, match currency naming convention
        """
        if currency not in self.currency_dict:
            self.currency_dict[currency] = CurrencyType.query.filter_by(name=currency).first()

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
        self.cause_of_death = reason
        super().destroy()


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
        self.id = kwargs.pop("id", None)  # This will be phased out
        self.has_storage = False
        super(StorageAgent, self).__init__(*args, **kwargs)
        for attr in self.attrs:
            if attr.startswith('char_capacity'):
                if not self.has_storage:
                    self.has_storage = True
                currency = attr.split('_', 2)[2]
                self.add_currency_to_dict(currency)
                initial_value = kwargs.get(currency, None)
                initial_value = initial_value if initial_value is not None else 0
                self._attr(currency, initial_value, is_client_attr=True, is_persisted_attr=True)
                # Actual capacity (storage_net_cap in GeneralAgent.step()) is
                # the capacity multiplied by the amount. We record the
                # individual capacity in case amount is decremented later.
                capacity = self.attrs[attr]
                self._attr(attr, capacity, is_client_attr=True, is_persisted_attr=True)

    def step(self):
        """TODO"""
        # Moved from agent_model to storages
        if self.has_storage:
            storage_id = self.agent_type
            if storage_id not in self.model.storage_ratios:
                self.model.storage_ratios[storage_id] = {}
            temp, total = {}, None
            for attr in self.attrs:
                if attr.startswith('char_capacity'):
                    currency = attr.split('_', 2)[2]
                    storage_unit = self.attr_details[attr]['units']
                    storage_value = pq.Quantity(float(self[currency]), storage_unit)
                    if not total:
                        total = storage_value
                    else:
                        storage_value.units = total.units
                        total += storage_value
                    temp[currency] = storage_value.magnitude.tolist()
            for currency in temp:
                if temp[currency] > 0:
                    self.model.storage_ratios[storage_id][currency + '_ratio'] = \
                        temp[currency] / total.magnitude.tolist()
                else:
                    self.model.storage_ratios[storage_id][currency + '_ratio'] = 0
        super().step()

    def view(self, view=None):
        currency_classes = ['atmo', 'sold', 'food', 'h2o', 'enrg']
        if view in currency_classes:
            currencies = [c for c in self.currency_dict if c.split('_')[0] == view]
            return {currency: self[currency] for currency in currencies}

    def kill(self, reason):
        """Destroys the agent and removes it from the model

        Args:
          reason: str, cause of death
        """
        self.destroy(reason)


class GeneralAgent(StorageAgent):
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
        self.has_flows = False
        super(GeneralAgent, self).__init__(*args, **kwargs)
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
        self.selected_storage = {"in": {}, 'out': {}}
        # NOTE: The 'agent_conn.json' file does not distinguish which agent
        # initiates a flow; e.g. a connection between 'greenhouse.atmo_co2' and
        # and 'rice.atmo_co2' could reference an INPUT of rice, or an OUTPUT of
        # greenhouse. The present function does that; rather than add all
        # the connections, we iterate through flows and add the appropriate
        # connection. In the future, it may be useful for diagnostic purposes
        # to copy all the connections (those initiated by an agent, and those
        # initiated by another). This shouldn't break anything.
        for attr in self.attrs:
            prefix, currency = attr.split('_', 1)
            if prefix not in ['in', 'out']:
                continue
            self.selected_storage[prefix][currency] = []
            if len(currency.split('_')) > 1:
                self.add_currency_to_dict(currency)
            connected_agents = self.connections[prefix][currency]
            for agent_type in connected_agents:
                storage_agent = self.model.get_agents_by_type(agent_type=agent_type)
                # Function returns a list, but with the latest updates, there
                # should only ever be one instance of an agent_type.
                storage_agent = storage_agent[0]
                self.selected_storage[prefix][currency].append(storage_agent)

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
            if not self.has_flows:
                self.has_flows = True
            agent_flow_time = self.attr_details[attr]['flow_time']
            lifetime_growth_type = self.attr_details[attr]['lifetime_growth_type']
            lifetime_growth_center = self.attr_details[attr]['lifetime_growth_center']
            lifetime_growth_min_value = self.attr_details[attr]['lifetime_growth_min_value']
            lifetime_growth_max_value = self.attr_details[attr]['lifetime_growth_max_value']
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
                max_value = lifetime_growth_max_value or 0.0
                center = lifetime_growth_center or None
                min_threshold = lifetime_growth_min_threshold or 0.0
                min_threshold *= num_values
                max_threshold = lifetime_growth_max_threshold or 0.0
                max_threshold *= num_values
                invert = bool(lifetime_growth_invert)
                noise = bool(lifetime_growth_noise)
                kwargs = {'agent_value': agent_value,
                          'max_value': max_value,
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
                    elif lifetime_growth_type:
                        kwargs['scale'] = 0.5
                        kwargs['max_value'] = agent_value * 1.1
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
                # For co2 management, criteria need to be evaluated against
                # specific storages; not all storages, as was done before.
                # I added '_in' or '_out' to the criteria name so that it can
                # be evaluated against a selected storage.
                source = 0
                direction = cr_name.split('_')[-1]
                storage_ratios = self.model.storage_ratios
                if direction in ['in', 'out']:
                    elements = cr_name.split('_')
                    currency = '_'.join(elements[:2])
                    cr_actual = '_'.join(elements[:3])
                    storage_id = self.selected_storage[direction][currency][0].agent_type
                    source += storage_ratios[storage_id][cr_actual]
                else:
                    for storage_id in storage_ratios:
                        if cr_name in storage_ratios[storage_id]:
                            source += storage_ratios[storage_id][cr_name]
            cr_id = '{}_{}_{}'.format(prefix, currency, cr_name)
            if cr_limit == '>':
                opp = operator.gt
            elif cr_limit == '<':
                opp = operator.lt
            elif cr_limit == '=':
                opp = operator.eq
            else:
                raise ServerError('Unknown attr criteria.')
            if opp(source, cr_value):
                if cr_buffer > 0 and self.buffer.get(cr_id, 0) > 0:
                    self.buffer[cr_id] -= 1
                    return pq.Quantity(0.0, agent_unit)
            else:
                if cr_buffer > 0:
                    self.buffer[cr_id] = cr_buffer
                return pq.Quantity(0.0, agent_unit)
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
        # If agent doesn't have flows (i.e. is storage agent), skip this step
        if not self.has_flows:
            return
        timedelta_per_step = self.model.timedelta_per_step()
        hours_per_step = timedelta_to_hours(timedelta_per_step)
        if self.age + hours_per_step >= self.lifetime > 0:
            self.grown = True
        # If agent has threshold characteristic, check value and kill if met.
        for attr in self.attrs:
            if attr.startswith('char_threshold_'):
                threshold_value = self.attrs[attr]
                threshold_type = attr.split('_', 3)[2]
                currency = attr.split('_', 3)[3]
                for prefix in ['in', 'out']:
                    if currency in self.selected_storage[prefix]:
                        for storage_agent in self.selected_storage[prefix][currency]:
                            agent_id = storage_agent.agent_type
                            if threshold_type == 'lower' and self.model.storage_ratios[agent_id][
                                currency + '_ratio'] < threshold_value:
                                self.kill('Threshold {} met for {}. Killing the agent'.format(
                                    currency, self.agent_type))
                                return
                            elif threshold_type == 'upper' and self.model.storage_ratios[agent_id][
                                currency + '_ratio'] > threshold_value:
                                self.kill('Threshold {} met for {}. Killing the agent'.format(
                                    currency, self.agent_type))
                                return
            # If agent has an extension function, e.g. 'atmosphere_equalizer', call it here.
            if attr == 'char_custom_function':
                custom_function_type = self.attrs[attr]
                custom_function = getattr(custom_funcs, custom_function_type)
                if custom_function:
                    custom_function(self)
                else:
                    raise Exception('Unknown custom function: f{custom_function}.')

        influx = set()
        skip_step = False
        # Iterate through all agent flows, starting with inputs
        for prefix in ['in', 'out']:
            # Iterate through all currencies for current flow direction
            for currency in self.selected_storage[prefix]:
                attr = '{}_{}'.format(prefix, currency)
                # TODO: Skip step if input/output value is set to 0. This was
                # added for atmosphere_equalizer, which uses 'dummy' in/outs to
                # trigger _init_selected_storage.
                if self.attrs[attr] == 0:
                    continue
                # Get the storages associated with this direction/currency
                num_of_storages = len(self.selected_storage[prefix][currency])
                if num_of_storages == 0:
                    self.kill('No storage of {} found for {}. Killing the agent'.format(
                        currency, self.agent_type))
                # Get values for DEPRIVE, REQUIRED and REQUIRES
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
                # INFLUX tracks input fields that are > 0 this step. Outputs
                # with a 'requires' field will reference this set and, if a
                # required input is missing, will be skipped.
                if len(requires) > 0 and len(set(requires).difference(influx)) > 0:
                    continue
                # Get VALUE based on values calculated by growth function
                step_value = self.get_step_value(attr)
                # NOTE Grant Oct 12'21: The old version assumed that flows were
                # split evenly between selected storages. Storages now use the
                # amount field rather than instances, so this calc is no longer
                # needed. HOWEVER, num_of_strages could be >1 if we include
                # storage priorities in a future update, so we retain the
                # ability to have multiple storages for a single currency.
                for storage in self.selected_storage[prefix][currency]:
                    value = agent_amount = 0
                    # This loop tries to execute a flow for the full amount
                    # of agents. If a currency in storage is lacking, it kills
                    # an agent, decrements the amount and tries again with one
                    # fewer agents. If a currency in storage is sufficient, it
                    # breaks the loop and continues.
                    # NOTE: Room for optimization in this process: find
                    # the available currency and jump straight to N surviving.
                    for i in range(self.amount, 0, -1):
                        # Get the maximum storage value, used to limit outputs
                        storage_cap = storage['char_capacity_' + currency]
                        storage_amount = storage.__dict__.get('amount', 1)
                        storage_net_cap = storage_cap * storage_amount
                        # Put step value into the same units as storage value
                        attr_name = 'char_capacity_' + currency
                        storage_unit = storage.attr_details[attr_name]['units']
                        storage_value = pq.Quantity(storage[currency], storage_unit)
                        step_value.units = storage_unit
                        # Calculate ideal new storage level
                        if prefix == 'in':
                            new_storage_value = storage_value - step_value * i
                        elif prefix == 'out':
                            new_storage_value = storage_value + step_value * i
                        else:
                            raise Exception('Unknown flow type. Neither Input nor Output.')
                        new_storage_value = new_storage_value.magnitude.tolist()
                        # If there ISN'T enough currency in the storage,
                        if new_storage_value < 0 <= storage_value:
                            if deprive_value > 0:
                                # Decrement the deprive value. If it hits 0,
                                # kill one agent and try again with one fewer.
                                self.deprive[currency] -= delta_per_step
                                if self.deprive[currency] < 0:
                                    self.amount -= 1
                                if self.amount <= 0:
                                    self.kill(f'All {self.agent_type} are died. Killing the agent')
                                    return
                            # If it's mandatory, abort step. This accounts for
                            # cases like the waste processor where, if there's
                            # no waste available, it shouldn't do anything.
                            if is_required == 'mandatory':
                                return
                            elif is_required == 'desired':
                                # NOTE: this seems to have no effect. It's only
                                # referenced once (a couple lines below), and
                                # whether it's true or false, the conditional
                                # will trigger because 'is_required' is truthy.
                                skip_step = True
                        # If there IS enough currency in storage,
                        else:
                            if not skip_step or is_required or self.attr_details[attr]['criteria_name']:
                                # Update the value of the storage.
                                # NOTE: If the output value is greater than the
                                # maximum capacity of the storage, the excess
                                # is currently ignored. This should be addressed.
                                storage[currency] = min(new_storage_value, storage_net_cap)
                                # If deprive is less than max, increment up.
                                # NOTE: This function takes the maximum as
                                # deprive value * amount, which doesn't seem
                                # to make sense?
                                if deprive_value > 0:
                                    self.deprive[currency] = min(deprive_value * self.amount,
                                                                 self.deprive[currency] +
                                                                 deprive_value)
                                agent_amount = i # NOTE: Redundant
                                value = float(step_value.magnitude.tolist()) * i
                                # Advance to the next step_num ONLY if the
                                # growth_criteria currency is increased.
                                # NOTE: The step_num defines the maximum growth
                                # potential at a point in the agent's lifetime.
                                # For plants, shouldn't this be related to the
                                # age of the plant, and not how much it's grown?
                                # In other words, if a plant is deprived of a
                                # required currency during its period of maximum
                                # growth, it shouldn't DELAY the maximum growth
                                # period until later, it should FORFEIT the
                                # maximum growth.
                                if attr == self.growth_criteria:
                                    self.agent_step_num += hours_per_step
                            break
                    # Values below a certain threshold (1e-12) are ignored.
                    if value > value_eps:
                        if prefix == 'in' and currency not in influx:
                            influx.add(currency)
                        currency_type = self.currency_dict[currency]
                        # Growth criteria updates the percentage grown, which
                        # is used at the end of life to calcuate outputs.
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
