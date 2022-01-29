import numpy as np
import json
import random
import pathlib

from agent_model.exceptions import AgentModelInitializationError
from agent_model.parse_data_files import parse_currency_desc, parse_agent_desc, \
                                         parse_agent_events, parse_agent_conn, merge_json

_DEFAULT_LOCATION = 'mars'
_DATA_FILES_DIR = pathlib.Path(__file__).parent.parent / 'data_files'
def load_data_file(fname):
    try:
        with open(_DATA_FILES_DIR / fname) as f:
            file = json.load(f)
        return file
    except FileNotFoundError:
        raise AgentModelInitializationError(f"File `{fname}` not found in {_DATA_FILES_DIR}.")

class AgentModelInitializer():
    """Contains all data required to initialize an AgentModel

    Attributes:
      model_data: dict, all data required to initialize an AgentModel
      agent_data: dict, all data required to initialize GeneralAgents
      init_type: str, 'from_new' or 'from_model'; indicates whether status
                 fields are included in model_data and agent_data

    Methods:
      from_new: Takes config and optional user-defined currencies, agents and
                connections, returns an AgentModelInitializer
      from_model: Takes an instantiated AgentModel, returns an
                  AgentModelInitialzier
      serialize: Converts this to a json-serializable dict
      deserialize: Converts from dict back into AgentModelInitializer

    Raises:
      AgentModelInitializationError
    """

    def __init__(self, model_data, agent_data, init_type):
        self.model_data = model_data
        self.agent_data = agent_data
        self.init_type = init_type

    def default_model_data():
        return dict(
            seed=random.getrandbits(32),
            global_entropy=0,
            single_agent=1,
            termination=[],
            priorities=[],
            location=_DEFAULT_LOCATION,
            minutes_per_step=60
        )

    @classmethod
    def from_new(cls, config, user_currency_desc=None, user_agent_desc=None,
                 user_agent_conn=None, user_agent_variation=None, user_agent_events=None):

        # 1. INITIALIZE ERROR DICT
        # Errors from all subsequent steps are compiled into a dict and returned to
        # user, for easier debugging.
        errors = dict(model={}, agents={}, currencies={})
        def _agent_error(agent, item, error):
            if agent not in errors['agents']:
                errors['agents'][agent] = {}
            errors['agents'][agent][item] = error

        # 2. INITIALIZE DEFAULT VALUES
        # Certain fields are required to run a simulation. If not specified
        # by user, use the default value.
        model_data = cls.default_model_data()
        for key, value in config.items():
            if key in ['agents', 'total_amount']:
                continue
            elif key in model_data:
                if key == 'seed':
                    if type(value) != int:
                        errors['model']['seed'] = 'seed must be an integer'
                        continue
                    value = value % 2**32
                model_data[key] = value
            else:
                errors['model'][key] = 'unrecognized'

        # LOAD AND MERGE DATA FILES
        # Default agent and currency parameters are specified in json files in
        # the `data_files` directory. User can specify custom parameters, which
        # will replace or be added to default values.

        # 3. CURRENCY DESC
        currency_desc = load_data_file('currency_desc.json')
        if user_currency_desc:
            currency_desc = merge_json(currency_desc, user_currency_desc)
        currency_desc, currency_errors = parse_currency_desc(currency_desc)
        model_data['currency_dict'] = currency_desc
        errors['currencies'] = currency_errors

        # 4. AGENT DESC
        agent_desc = load_data_file('agent_desc.json')
        if user_agent_desc:
            agent_desc = merge_json(agent_desc, user_agent_desc)
        # Only return agent_desc data for agents included in the config file
        agent_desc, agents_errors = parse_agent_desc(config, model_data['currency_dict'], agent_desc, _DEFAULT_LOCATION)
        errors['agents'] = agents_errors

        # 5. AGENT EVENTS
        agent_events = load_data_file('agent_events.json')
        if user_agent_events:
            agent_events = merge_json(agent_events, user_agent_events)
        agents_events, agents_errors = parse_agent_events(agent_events)
        for agent, errors in agents_errors.items():
            for item, message in errors.items():
                _agent_error(agent, item, message)
        for agent, agent_data in agent_desc.items():
            if agent in agents_events:
                events = agents_events[agent]
            elif agent_data['agent_class'] in agents_events:
                events = agents_events[agent_data['agent_class']]
            else:
                continue
            for section in ['attributes', 'attribute_details']:
                agent_data[section] = {**agent_data[section], **events[section]}

        # 6. AGENT VARIATION
        agent_variation = load_data_file('agent_variation.json')
        if user_agent_variation:
            agent_variation = merge_json(agent_variation, user_agent_variation)
        for agent, agent_data in agent_desc.items():
            if agent in agent_variation:
                variation = agent_variation[agent]['variation']
            elif agent_data['agent_class'] in agent_variation:
                variation = agent_variation[agent_data['agent_class']]
            else:
                continue
            valid_variation = {}
            for key, value in variation.items():
                if key not in ['initial', 'step']:
                    _agent_error(agent, 'variation', f"Unrecognized variation type: {key}")
                valid_variation[key] = value
            if len(valid_variation) == 0:
                _agent_error(agent, 'variation', f"No valid variation types found")
            else:
                agent_data['variation'] = valid_variation

        # 7. AGENT CONNECTIONS
        agent_conn = load_data_file('agent_conn.json')
        if user_agent_conn:
            # TODO: This approach may fail if trying to *replace* a connection
            # with user_agent_conn.
            agent_conn = user_agent_conn + agent_conn
        active_agents = list(config['agents'].keys())
        connections, agent_conn_errors = parse_agent_conn(active_agents, agent_conn)
        for agent, error in agent_conn_errors.items():
            _agent_error(agent, 'connection', error)
        for a in active_agents:
            config['agents'][a]['connections'] = {} if a not in connections else connections[a]

        # Build and validate agent instance
        agent_data = {}
        if len(config['agents']) == 0:
            errors['model']['agents'] = "Must specify at least one agent"
        for agent, instance in config['agents'].items():
            if agent not in agent_desc:
                continue
            valid_instance = {}
            non_currency_fields = ['id', 'amount', 'total_capacity', 'connections', 'delay_start']
            for field, value in instance.items():
                if field not in non_currency_fields and field not in model_data['currency_dict']:
                    _agent_error(agent, field, "Unrecognized field in agent instance")
                else:
                    valid_instance[field] = value
            agent_data[agent] = dict(agent_desc=agent_desc[agent], instance=valid_instance)

        return cls(model_data, agent_data, 'from_new'), errors

    @classmethod
    def from_model(cls, model):
        model_data = dict(
            # Metadata (optional, set externally)
            user_id=model.user_id,
            game_id=model.game_id,
            start_time=model.start_time,
            # Configuration (user-input)
            seed=model.seed,
            global_entropy=model.global_entropy,
            single_agent=model.single_agent,
            termination=model.termination,
            priorities=model.priorities,
            location=model.location,
            minutes_per_step=model.minutes_per_step,
            currency_dict=model.currency_dict,
            # Status (generated)
            random_state=model.random_state.get_state(),
            time=model.time.seconds,  # int of seconds
            steps=model.scheduler.steps,
            storage_ratios=model.storage_ratios,
            step_records_buffer=model.step_records_buffer,
            is_terminated=model.is_terminated,
            termination_reason=model.termination_reason,
        )

        agent_data = {}
        for agent in model.scheduler.agents:
            agent_data[agent['agent_type']] = cls._from_agent(agent)

        return cls(model_data, agent_data, 'from_model')

    def _from_agent(agent):
        agent_desc = dict(
            agent_class=agent.agent_class,
            agent_type_id=agent.agent_type_id,
            attributes=agent.attrs,
            attribute_details=agent.attr_details
        )
        instance = dict(
            # BaseAgent
            unique_id=agent.unique_id,
            active=agent.active,
            age=agent.age,
            amount=agent.amount,
            initial_variable=agent.initial_variable,
            step_variation=agent.step_variation,
            step_variable=agent.step_variable,
            # StorageAgent
            id=agent.id,
            # GeneralAgent
            connections=agent.connections,
            buffer=agent.buffer,
            deprive=agent.deprive,
            step_values={},
            events=agent.events,
            event_multipliers=agent.event_multipliers
        )
        # PlantAgent
        if agent.agent_class == 'plants':
            plant_fields = dict(
                delay_start=agent.delay_start,
                agent_step_num=agent.agent_step_num,
                full_amount=agent.full_amount,
                total_growth=agent.total_growth,
                current_growth=agent.current_growth,
                growth_rate=agent.growth_rate,
                grown=agent.grown,
            )
            instance = {**instance, **plant_fields}
        # Step values
        for currency, step_values in agent.step_values.items():
            instance['step_values'][currency] = step_values
        # Storage balances
        for item in agent.__dict__.keys():
            if item in agent.currency_dict:
                if agent.currency_dict[item]['type'] == 'currency':
                    instance[item] = agent[item]

        return dict(agent_desc=agent_desc, instance=instance)

    def serialize(self):
        # Serialize np arrays
        if 'random_state' in self.model_data:
            r0, r1, r2, r3, r4 = self.model_data['random_state']
            self.model_data['random_state'] = (r0, r1.tolist(), r2, r3, r4)
        for agent_data in self.agent_data.values():
            if 'step_values' in agent_data['instance']:
                step_values = {}
                for currency, values in agent_data['instance']['step_values'].items():
                    step_values[currency] = values.tolist()
                agent_data['instance']['step_values'] = step_values

        return dict(model_data=self.model_data,
                    agent_data=self.agent_data,
                    init_type=self.init_type)

    @classmethod
    def deserialize(cls, serialized):
        # Initialize new initializer
        init = cls(serialized['model_data'], serialized['agent_data'],
                   serialized['init_type'])

        # Deserialize np arrays
        r0, r1, r2, r3, r4 = init.model_data['random_state']
        r1 = np.ndarray((624), dtype='uint64', buffer=np.array(r1))
        init.model_data['random_state'] = (r0, r1, r2, r3, r4)
        for agent_data in init.agent_data.values():
            step_values = {}
            for currency, values in agent_data['instance']['step_values'].items():
                step_values[currency] = np.array(values)
            agent_data['instance']['step_values'] = step_values

        return init

