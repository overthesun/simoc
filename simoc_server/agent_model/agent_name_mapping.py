from .human import HumanAgent
from .plants import PlantAgent

agent_name_mapping = {}

def _add_all():
    _add_agent_class_to_mapping(HumanAgent)
    _add_agent_class_to_mapping(PlantAgent)

def _add_agent_class_to_mapping(AgentCls):
    agent_name_mapping[AgentCls.__agent_type_name__]  = AgentCls

_add_all()