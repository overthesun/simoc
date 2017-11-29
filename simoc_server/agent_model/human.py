from .baseagent import BaseAgent

class HumanAgent(BaseAgent):
    __agent_type_name__ = "Human"
    #__sprite_mapper__ = HumanSpriteMapper

    def init_new(self):
        self.energy = self.get_agent_type_attribute("max_energy")


HumanAgent.__persisted_attributes__.add("energy")
HumanAgent.__client_attributes__.add("energy")