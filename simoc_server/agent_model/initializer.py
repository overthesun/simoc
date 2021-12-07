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
    """Contains all data required to initialize an AgentModel"""

    def __init__(self, model_data, agent_data):
        self.model_data = model_data
        self.agent_data = agent_data

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
        model_data['currencies'] = parse_currency_desc(default_currency_desc)
        agent_desc = parse_agent_desc(config, model_data['currencies'], default_agent_desc)

        # Unpack and initialize agent-level fields
        agent_data = {}
        for agent, instance in config['agents'].items():
            non_currency_fields = ['id', 'amount', 'total_capacity', 'connections']
            for field in instance:
                if field not in non_currency_fields and field not in model_data['currencies']:
                    raise AgentModelInitializationError(f"Currency {field} specified for agent {agent} not found in currency dict.")
            agent_data[agent] = dict(agent_desc=agent_desc[agent], instance=instance)

        return AgentModelInitializer(model_data, agent_data)

    def from_model(model):
        model_data = dict(
            currency_dict=model.currency_dict,
            start_time=model.start_time,
            game_id=model.game_id,
            user_id=model.user_id,
            seed=model.seed,
            random_date=model.random_state,
            termination=model.termination,
            termination_reason=model.termination_reason,
            single_agent=model.single_agent,
            priorities=model.priorities,
            location=model.location,
            config=model.config,
            time=model.time,
            minutes_per_step=model.minutes_per_step,
            is_terminated=model.is_terminated,
            storate_ratios=model.storage_ratios,
            day_length_minutes=model.day_length_minutes,
            daytime=model.daytime,
            steps=model.scheduler.steps,
        )

        agent_data = {}
        for agent in model.scheduler.agents:
            agent_data[agent['agent_type']] = agent.save()

        return AgentModelInitializer(model_data, agent_data)

    def serialize(self):
        return dict(model_data=self.model_data, agent_data=self.agent_data)
