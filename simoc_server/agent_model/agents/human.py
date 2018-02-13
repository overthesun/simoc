import math
import datetime

from simoc_server.util import timedelta_to_days
from .baseagent import BaseAgent

class HumanAgent(BaseAgent):

    _agent_type_name = "human"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attr("energy", 1.0, is_client_attr=True, is_persisted_attr=True)
        # Todo change this to _type Structure after merge
        self._attr("structure", None, _type=BaseAgent, is_client_attr=True, is_persisted_attr=True)


    def step(self):
        timedelta_per_step = self.model.timedelta_per_step()

        days_elapsed = timedelta_to_days(timedelta_per_step)

        #self.model.water -= self.total_water_usage_per_day() * days_elapsed
        #self.model.waste_water += 


    def total_water_usage_per_day():
        try:
            # try cached value
            return self._total_water_usage_per_day
        except AttributeError as ex:
            consumed = get_agent_type_attribute("consumed_water_usage")
            hygiene = get_agent_type_attribute("hygiene_water_usage")
            medical = get_agent_type_attribute("medical_water_usage")

            self._total_water_usage_per_day = consumed + hygiene + medical
            return self._total_water_usage_per_day
