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
            currency_data = self.model.currency_dict[currency]
            self.currency_dict[currency] = currency_data
            if currency_data['type'] == 'currency':
                self.add_currency_to_dict(currency_data['class'])

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
        class_capacities = {}
        class_units = {}
        for attr in self.attrs:
            if attr.startswith('char_capacity'):
                if not self.has_storage:
                    self.has_storage = True
                currency = attr.split('_', 2)[2]
                self.add_currency_to_dict(currency)
                initial_value = kwargs.get(currency, None)
                initial_value = initial_value if initial_value is not None else 0
                self._attr(currency, initial_value, is_client_attr=True, is_persisted_attr=True)
                capacity = self.attrs[attr]
                self._attr(attr, capacity, is_client_attr=True, is_persisted_attr=True)
                # Add meta-attributes for currency classes, so that inputs/outputs
                # can use the same mechanisms to reference them.
                currency_class = self.currency_dict[currency]['class']
                if currency_class not in class_capacities:
                    class_capacities[currency_class] = 0
                    class_units[currency_class] = self.attr_details[attr]['units']
                class_capacities[currency_class] += capacity
        for currency_class, capacity in class_capacities.items():
            class_attr = 'char_capacity_' + currency_class
            self._attr(class_attr, capacity, is_client_attr=True, is_persisted_attr=True)
            self.attr_details[class_attr] = dict(units=class_units[currency_class])

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
        if view not in self.currency_dict:
            raise KeyError(f"{view} is not a recognized view.")
        currency_data = self.currency_dict[view]
        if currency_data['type'] == 'currency':
            currency = view
            return {currency: self[currency]}
        elif currency_data['type'] == 'currency_class':
            currencies = currency_data['currencies']
            return {c: self[c] for c in currencies if c in self}
        else:
            raise KeyError(f"Currency {currency_data['name']} type not recognized by view.")

    def increment(self, view, increment_amount):
        """Increase or decrease storage balances

        If increment amount is positive, the view must be a currency and amount
        is limited by storage capacity.

        If increment is negative, view may be currency or currency_class. If
        currency_class, split amount between available currencies of class in
        proportion to their current balance.

        Return a dict with currency:value pairs of the actual amount
        incremented.

        """
        if increment_amount > 0:
            currency = view
            if self.currency_dict[currency]['type'] != 'currency':
                raise ValueError(f"Positive increment can only be used with currencies.")
            capacity = self['char_capacity_' + currency] * self.amount
            currency_amount = min(self[currency] + increment_amount, capacity)
            currency_increment_actual = self[currency] - currency_amount
            self[currency] = currency_amount
            return {currency: currency_increment_actual}
        elif increment_amount < 0:
            currencies = self.view(view)
            total_view_amount = sum(currencies.values())
            target_view_amount = total_view_amount + increment_amount
            if target_view_amount < 0:
                raise ValueError(f"{self.agent_type} has insufficient {view} balance to increment by {increment_amount}")
            ratios = {c: self[c]/total_view_amount for c in currencies.keys()}
            flow = {}
            for currency in currencies:
                currency_increment_target = increment_amount * ratios[currency]
                currency_amount = max(self[currency] + currency_increment_target, 0)
                currency_increment_actual = self[currency] - currency_amount
                self[currency] = currency_amount
                flow[currency] = currency_increment_actual
            return flow
        else:
            return {}

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
            connected_agents = self.connections[prefix][currency]
            if len(connected_agents) == 0:
                raise Exception(f"No connection specified for {self.agent_type!r} {currency!r}.")
            self.selected_storage[prefix][currency] = []
            self.add_currency_to_dict(currency)
            attr_name = 'char_capacity_' + currency
            attr_units = None
            for agent_type in connected_agents:
                # Function returns a list, but with the latest updates, there
                # should only ever be one instance of an agent_type.
                storage_agent = self.model.get_agents_by_type(agent_type=agent_type)
                storage_agent = storage_agent[0]
                storage_units = storage_agent.attr_details[attr_name]['units']
                if attr_units:
                    if storage_units != attr_units:
                        raise Exception(f"Connections for {self.agent_type!r} {currency!r} have same units.")
                else:
                    attr_units = storage_units
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
                self.last_flow = {}
                self.flows = {}
            self.last_flow[currency] = 0
            self.flows[currency] = []
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
                    currency = elements[0]
                    cr_actual = '_'.join(elements[:2])
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
                if len(requires) > 0 and len(set(requires).difference(influx)) > 0:
                    continue
                target_value = self.get_step_value(attr)
                actual_value = 0
                agent_amount = 0
                # Determine the available_value based on storage balances
                available_value = 0   # Available in connected storages
                available_conns = []  # Breakdown of values by connection
                for storage in self.selected_storage[prefix][currency]:
                    attr_name = 'char_capacity_' + currency
                    storage_unit = storage.attr_details[attr_name]['units']
                    storage_value = sum(storage.view(currency).values())
                    available_value += storage_value
                    target_value.units = storage_unit
                    storage_cap = storage[attr_name]
                    storage_amount = storage.__dict__.get('amount', 1)
                    storage_net_cap = storage_cap * storage_amount
                    available_conns.append(dict(agent=storage, value=storage_value,
                                                capacity=storage_net_cap))

                # This loop tries to execute a flow for the full amount
                # of agents. If a currency in storage is lacking, it updates
                # deprive or kills an agent, decrements the amount and tries
                # again with one fewer agents. If a currency in storage is
                # sufficient, it breaks the loop and continues.
                # NOTE: Room for optimization in this process: find
                # the available currency and jump straight to N surviving.
                for i in range(self.amount, 0, -1):
                    test_value = target_value.magnitude.tolist() * i
                    if prefix == 'in':
                        new_storage_value = available_value - test_value
                    elif prefix == 'out':
                        new_storage_value = available_value + test_value
                    # If there ISN'T enough currency in the storage
                    # (excluding storages that were empty, i.e. output targets)
                    if new_storage_value < 0 <= available_value:
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
                            remaining_value = test_value
                            flows = []
                            for conn in available_conns:
                                storage = conn['agent']
                                if prefix == 'in':
                                    conn_delta = min(remaining_value, conn['value'])
                                    flow = storage.increment(currency, -conn_delta)
                                elif prefix == 'out':
                                    conn_delta = remaining_value / len(available_conns)
                                    flow = storage.increment(currency, conn_delta)
                                remaining_value -= conn_delta
                                for k, v in flow.items():
                                    if v == 0:
                                        continue
                                    flows.append({"storage_type": storage.agent_type,
                                                  "storage_type_id": storage.agent_type_id,
                                                  "storage_agent_id": storage.unique_id,
                                                  "storage_id": storage.id,
                                                  "currency": k,
                                                  "amount": v})
                                if remaining_value <= 0:
                                    break
                            # If deprive is less than max, increment up.
                            # NOTE: This function takes the maximum as
                            # deprive value * amount, which doesn't seem
                            # to make sense?
                            if deprive_value > 0:
                                self.deprive[currency] = min(deprive_value * self.amount,
                                                             self.deprive[currency] +
                                                             deprive_value)
                            agent_amount = i
                            actual_value = test_value
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
                if actual_value > value_eps:
                    if prefix == 'in' and currency not in influx:
                        influx.add(currency)
                    currency_data = self.currency_dict[currency]
                    # Growth criteria updates the percentage grown, which
                    # is used at the end of life to calcuate outputs.
                    if attr == self.growth_criteria:
                        self.current_growth += (actual_value / agent_amount)
                        self.growth_rate = self.current_growth / self.total_growth
                        growth = self.growth_rate
                    else:
                        growth = None
                    self.last_flow[currency] = actual_value
                    self.flows[currency] = flows
                    for flow in flows:
                        record = {"step_num": self.model.step_num + 1,
                                  "game_id": self.model.game_id,
                                  "user_id": self.model.user_id,
                                  "agent_type": self.agent_type,
                                  "agent_type_id": self.agent_type_id,
                                  "agent_id": self.unique_id,
                                  "direction": prefix,
                                  "agent_amount": agent_amount,
                                  "currency_type": flow['currency'],
                                  "currency_type_id": self.model.currency_dict[flow['currency']]['id'],
                                  "value": abs(round(flow['amount'], value_round)),
                                  "growth": growth,
                                  "unit": str(target_value.units),
                                  "storage_type": flow['storage_type'],
                                  "storage_type_id": flow['storage_type_id'],
                                  "storage_agent_id": flow['storage_agent_id'],
                                  "storage_id": flow['storage_id']}
                        self.model.step_records_buffer.append(record)

    def kill(self, reason):
        """Destroys the agent and removes it from the model

        Args:
          reason: str, cause of death
        """
        self.destroy(reason)
