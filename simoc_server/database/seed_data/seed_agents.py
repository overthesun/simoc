from . import util
from collections import OrderedDict
from simoc_server.database.db_model import AgentType, AgentTypeAttribute


def seed():
    human_data = gen_human()

    util.add_all(human_data)



def gen_human():
    data = OrderedDict()
    data["human_agent_type"] = AgentType(name="Human")
    data["human_max_energy_attr"] = create_agent_type_attr(data["human_agent_type"], "max_energy", 100)

    return data

def create_agent_type_attr(agent_type, name, value):
    return AgentTypeAttribute(name=name, agent_type=agent_type, value=value,
        value_type=str(type(value).__name__))