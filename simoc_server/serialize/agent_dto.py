from simoc_server.agent_model.agents import BaseAgent
from . import BaseDTO

class AgentDTO(BaseDTO):

    def __init__(self, agent):
        self.agent = agent

    def get_state(self):
        state = {
            "id":self.agent.unique_id,
            "agent_type":self.agent.__class__._agent_type_name,
        }

        if hasattr(self.agent, "pos"):
            state["pos_x"] = self.agent.pos[0],
            state["pos_y"] = self.agent.pos[1],

        attributes = {}
        for attribute_name, attribute_descriptor in self.agent.attribute_descriptors.items():
            if attribute_descriptor.is_client_attr:
                attribute_value = self.agent.__dict__[attribute_name]
                if(issubclass(attribute_descriptor._type, BaseAgent) and attribute_value is not None):
                    attributes[attribute_name] = attribute_value.unique_id
                else:    
                    attributes[attribute_name] = attribute_value
        state["attributes"] = attributes
        return state

    def get_state_with_diff(self, prev_state=None):
        state = self.get_state()
        if prev_state is None:
            return state, {}
        else:
            diff = {}
            if hasattr(self.agent, "pos"):
                if state["pos_x"] != prev_state["pos_x"]:
                    diff["pos_x"] = state["pos_x"]
                if state["pos_y"] != prev_state["pos_y"]:
                    diff["pos_y"] = state["pos_y"]
            attributes = state["attributes"]
            prev_attributes = prev_state["attributes"]
            attr_diff = {(key, val) for key, val in attributes if val != prev_state[key]}
            diff["attributes"] = attr_diff
            return state, diff