import json
import random
import pathlib

from simoc_server.exceptions import AgentModelInitializationError
from simoc_server.agent_model.parse_data_files import parse_currency_desc, parse_agent_desc

_DATA_FILES_DIR = pathlib.Path(__file__).parent.parent.parent / 'data_files'
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

    Raises:
      AgentModelInitializationError
    """

    def __init__(self, model_data, agent_data, init_type):
        self.model_data = model_data
        self.agent_data = agent_data
        self.init_type = init_type

    def from_new(config, user_currency_desc=None, user_agent_desc=None,
                 user_agent_conn=None):

        # Unpack & initialize all model-level fields from config
        model_data = dict(
            seed=config.get('seed', random.getrandbits(32)),
            single_agent=0 if not config.get('single_agent', None) == 1 else 1,
            termination=config.get('termination', []),
            priorities=config.get('priorities', []),
            location=config.get('location', 'mars'),
            total_amount=config.get('total_amount', len(config['agents'])),
            minutes_per_step=config.get('minutes_per_step', 60),
        )

        # Load and merge data files
        default_currency_desc = load_data_file('currency_desc.json')
        default_agent_desc = load_data_file('agent_desc.json')
        # TODO: Add connections here, rather than in convert_config
        # TODO: Merge with user-defined
        model_data['currency_dict'] = parse_currency_desc(default_currency_desc)
        agent_desc = parse_agent_desc(config, model_data['currency_dict'], default_agent_desc)

        # Unpack and initialize agent-level fields
        agent_data = {}
        for agent, instance in config['agents'].items():
            non_currency_fields = ['id', 'amount', 'total_capacity', 'connections']
            for field in instance:
                if field not in non_currency_fields and field not in model_data['currency_dict']:
                    raise AgentModelInitializationError(f"Currency {field} specified for agent {agent} not found in currency dict.")
            agent_data[agent] = dict(agent_desc=agent_desc[agent], instance=instance)

        return AgentModelInitializer(model_data, agent_data, 'from_new')

    def from_model(model):
        model_data = dict(
            # Metadata (optional, set externally)
            user_id=model.user_id,
            game_id=model.game_id,
            start_time=model.start_time,
            # Configuration (user-input)
            seed=model.seed,
            single_agent=model.single_agent,
            termination=model.termination,
            priorities=model.priorities,
            location=model.location,
            total_amount=model.total_amount,
            minutes_per_step=model.minutes_per_step,
            currency_dict=model.currency_dict,
            # Status (generated)
            random_state=model.random_state.get_state(),  # type np.random.RandomState()
            time=repr(model.time),  # type datetime.timedelta
            steps=model.scheduler.steps,
            storage_ratios=model.storage_ratios,
            step_records_buffer=model.step_records_buffer,
            is_terminated=model.is_terminated,
            termination_reason=model.termination_reason,
        )

        agent_data = {}
        for agent in model.scheduler.agents:
            agent_data[agent['agent_type']] = agent.save()

        return AgentModelInitializer(model_data, agent_data, 'from_model')
