from .base_dto import BaseDTO

class AgentDTO(BaseDTO):

    def __init__(self, agent):
        self.agent = agent

    def get_state(self):
        # TODO implement
        pass

    def get_state_diff(self, prev_state):
        # TODO implement
        pass