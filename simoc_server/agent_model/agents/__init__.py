from simoc_server.agent_model.agents.human import HumanAgent
from simoc_server.agent_model.agents.plants import PlantAgent
from simoc_server.agent_model.agents.core import BaseAgent, EnclosedAgent
from simoc_server.agent_model.agents.structure import (PlumbingSystem, Atmosphere, Structure,
    Airlock, CrewQuarters, Greenhouse, Kitchen, PowerStation, RocketPad, RoverDock, StorageFacility)

# Until a better solution can be found, agents must be imported here and added to the below list

_agent_classes = [HumanAgent, PlantAgent, BaseAgent, EnclosedAgent,PlumbingSystem, Atmosphere, 
    Structure, Airlock, CrewQuarters, Greenhouse, Kitchen, PowerStation, RocketPad, RoverDock, StorageFacility]




agent_name_mapping = {}

def _add_all():
    for c in _agent_classes:
        _add_agent_class_to_mapping(c)


def _add_agent_class_to_mapping(AgentCls):
    agent_name_mapping[AgentCls._agent_type_name]  = AgentCls

def get_agent_by_type_name(name):
    try:
        return agent_name_mapping[name]
    except KeyError as ex:
        raise Exception("Cannot find agent with requested type name: {}".format(name))

_add_all()
del _add_all