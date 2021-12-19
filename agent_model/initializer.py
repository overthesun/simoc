import numpy as np
import json
import random
import pathlib

from agent_model.exceptions import AgentModelInitializationError
from agent_model.parse_data_files import parse_currency_desc, parse_agent_desc

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

    @classmethod
    def from_new(cls, config, user_currency_desc=None, user_agent_desc=None,
                 user_agent_conn=None, user_agent_variation=None):

        # Unpack & initialize all model-level fields from config
        seed = config.get('seed', None)
        seed = seed if type(seed) == int else random.getrandbits(32)
        seed = seed if seed > 2**32 else seed % 2**32
        model_data = dict(
            seed=seed,
            global_entropy=config.get('global_entropy', None),
            single_agent=0 if not config.get('single_agent', None) == 1 else 1,
            termination=config.get('termination', []),
            priorities=config.get('priorities', []),
            location=config.get('location', _DEFAULT_LOCATION),
            total_amount=config.get('total_amount', len(config['agents'])),
            minutes_per_step=config.get('minutes_per_step', 60),
        )

        # Load and merge data files
        default_currency_desc = load_data_file('currency_desc.json')
        default_agent_desc = load_data_file('agent_desc.json')
        # TODO: Add connections here, rather than in convert_config
        # TODO: Merge with user-defined
        model_data['currency_dict'] = parse_currency_desc(default_currency_desc)
        agent_desc = parse_agent_desc(config, model_data['currency_dict'], default_agent_desc, _DEFAULT_LOCATION)

        # Add agent variation data
        if model_data['global_entropy']:
            default_agent_variation = load_data_file('agent_variation.json')
            for agent, agent_data in agent_desc.items():
                if agent_data['agent_class'] in default_agent_variation:
                    agent_data['variation'] = default_agent_variation[agent_data['agent_class']]

        # Unpack and initialize agent-level fields
        agent_data = {}
        for agent, instance in config['agents'].items():
            non_currency_fields = ['id', 'amount', 'total_capacity', 'connections']
            for field in instance:
                if field not in non_currency_fields and field not in model_data['currency_dict']:
                    raise AgentModelInitializationError(f"Currency {field} specified for agent {agent} not found in currency dict.")
            agent_data[agent] = dict(agent_desc=agent_desc[agent], instance=instance)

        return cls(model_data, agent_data, 'from_new')

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
            total_amount=model.total_amount,
            minutes_per_step=model.minutes_per_step,
            currency_dict=model.currency_dict,
            # Status (generated)
            random_state=model.random_state.get_state(),
            time=repr(model.time),  # type datetime.timedelta
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
            # GrowthAgent
            age=agent.age,
            amount=agent.amount,
            full_amount=agent.full_amount,
            agent_step_num=agent.agent_step_num,
            total_growth=agent.total_growth,
            current_growth=agent.current_growth,
            growth_rate=agent.growth_rate,
            grown=agent.grown,
            # StorageAgent
            id=agent.id,
            # GeneralAgent
            connections=agent.connections,
            buffer=agent.buffer,
            deprive=agent.deprive,
            step_values={}
        )
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
        r0, r1, r2, r3, r4 = self.model_data['random_state']
        self.model_data['random_state'] = (r0, r1.tolist(), r2, r3, r4)
        for agent_data in self.agent_data.values():
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
        r1 = np.ndarray((624), buffer=np.array(r1))
        init.model_data['random_state'] = (r0, r1, r2, r3, r4)
        for agent_data in init.agent_data.values():
            step_values = {}
            for currency, values in agent_data['instance']['step_values'].items():
                step_values[currency] = np.array(values)
            agent_data['instance']['step_values'] = step_values

        return init

