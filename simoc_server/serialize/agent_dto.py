from . import BaseDTO

class AgentDTO(BaseDTO):

    def __init__(self, agent):
        self.agent = agent

    def get_state(self):
        state = {
            "pos_x":self.agent.pos[0],
            "pos_y":self.agent.pos[1]
        }

        attributes = {}
        for name in self.agent.client_attributes:
            attributes[name] = self.agent.__dict__[name]
        state["attributes"] = attributes
        return state

    def get_state_diff(self, prev_state):
        # TODO implement
        pass