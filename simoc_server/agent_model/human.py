import math
from .baseagent import BaseAgent
from .plants import PlantAgent

class HumanAgent(BaseAgent):

    __agent_type_name__ = "human" #__sprite_mapper__ = HumanSpriteMapper

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attr("health", 1.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("energy", 1.0, is_client_attr=True, is_persisted_attr=True)
