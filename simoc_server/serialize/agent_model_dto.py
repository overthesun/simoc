from . import BaseDTO, AgentDTO

class AgentModelDTO(BaseDTO):

    def __init__(self, agent_model):
        self.agent_model = agent_model

    def get_state(self):
        state = {
            "step_num":self.agent_model.step_num,
        }

        agents = []
        for agent in self.agent_model.scheduler.agents:
            agents.append(AgentDTO(agent).get_state())
        state["agents"] = agents

        return state

    def get_state_diff(self, prev_state):
        # TODO implement
        pass