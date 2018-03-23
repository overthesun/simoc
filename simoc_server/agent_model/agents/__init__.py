from simoc_server.agent_model.agents.human import HumanAgent

from simoc_server.agent_model.agents.plants import (PlantAgent, CabbageAgent, CarrotAgent, ChardAgent, 
    DryBeanAgent, LettuceAgent, PeaAgent, PeanutAgent, PepperAgent, RedBeetAgent, RiceAgent, SnapBeanAgent, 
    SoybeanAgent, SpinachAgent, StrawberryAgent, SweetPotatoAgent, TomatoAgent, WheatAgent, WhitePotatoAgent)

from simoc_server.agent_model.agents.core import BaseAgent, EnclosedAgent

from simoc_server.agent_model.agents.structure import (PowerModule, PlumbingSystem, Atmosphere, Structure,
    Airlock, CrewQuarters, Greenhouse, Kitchen, PowerStation, RocketPad, RoverDock, StorageFacility, Planter, Harvester,
    StoredMass, StoredFood)

from simoc_server.agent_model.agents.eclss import CarbonScrubber

# Until a better solution can be found, agents must be imported here and added to the below list

# core agents + human
_agent_classes = [ BaseAgent, EnclosedAgent, HumanAgent ]

# structure agents
_agent_classes += [ PowerModule, PlumbingSystem, Atmosphere, Structure, Airlock, CrewQuarters, 
    Greenhouse, Kitchen, PowerStation, RocketPad, RoverDock, StorageFacility, Harvester, Planter,
    StoredMass, StoredFood ]

# plant agents
_agent_classes += [ PlantAgent, CabbageAgent, CarrotAgent, ChardAgent, 
    DryBeanAgent, LettuceAgent, PeaAgent, PeanutAgent, PepperAgent, RedBeetAgent, RiceAgent, SnapBeanAgent, 
    SoybeanAgent, SpinachAgent, StrawberryAgent, SweetPotatoAgent, TomatoAgent, WheatAgent, WhitePotatoAgent ]

# eclss agents
_agent_classes += [CarbonScrubber]

# equipment agents
#_agent_classes +=[Equipment, PowerModule]

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


