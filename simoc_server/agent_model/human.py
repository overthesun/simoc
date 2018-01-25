import math
from .baseagent import BaseAgent
from .plants import PlantAgent

class HumanAgent(BaseAgent):

    __agent_type_name__ = "human" #__sprite_mapper__ = HumanSpriteMapper

    def init_new(self):
        self.health = 1.0
        self.energy = 1.0
