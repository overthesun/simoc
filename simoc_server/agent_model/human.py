from .baseagent import BaseAgent

class HumanAgent(BaseAgent):
    __agent_type_name__ = "Human"

    def init_new(self):
        self.energy = self.get_agent_type_attribute("max_energy")

        self.register_persisted_attribute("energy")
        self.register_client_attribute("energy")

        #self.sprite_mapper = AstronautSpriteMapper
