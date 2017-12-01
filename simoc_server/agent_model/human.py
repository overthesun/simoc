from .baseagent import BaseAgent

class HumanAgent(BaseAgent):
    
    __agent_type_name__ = "Human"
    #__sprite_mapper__ = HumanSpriteMapper
    __status__ = {
        "Standby": "Standby",
        "Working": "Working",
        "Sleeping": "Sleeping",
        "Relaxing": "Relaxing",
        "Exporing" : "Exporing"
        }
    
    def init_new(self):
        self.thirst = 100
        self.hunger = 100
        self.happiness = 100
        self.health = 100
        self.status = HumanAgent.status["Standby"]
        self.destination_position = 0, 0
        self.energy = self.get_agent_type_attribute("max_energy") #calories to burn
    
    def step(self):
        
        pass

    def move(self):
        pass

    def eat(self):
        self.hunger += 1
        pass

    def drink(self):
        self.thirst += 1
        pass

    def sleep(self):
        self.status = HumanAgent.status["Sleeping"]
        pass
    
HumanAgent.__persisted_attributes__.add("energy")
HumanAgent.__client_attributes__.add("energy")
