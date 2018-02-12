import math
from .baseagent import BaseAgent

class HumanAgent(BaseAgent):

    _agent_type_name = "human"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attr("health", 1.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("energy", 1.0, is_client_attr=True, is_persisted_attr=True)
