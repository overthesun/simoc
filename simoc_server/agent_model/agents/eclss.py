from simoc_server.agent_model.agents.core import EnclosedAgent
from simoc_server.util import timedelta_to_days

class CarbonScrubber(EnclosedAgent):
    _agent_type_name = "carbon_scrubber"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        power_consumption = self.get_agent_type_attribute("power_consumption")
        self._attr("power_consumption", default_value=power_consumption, is_persisted_attr=True, is_client_attr=True)
        self._attr("is_active", default_value=False, is_persisted_attr=False, is_client_attr=True)
        self._attr("powered", default_value=True, is_persisted_attr=True, is_client_attr=True)

    def step(self):
        if self.powered:
            atmosphere = self.structure.atmosphere
            days_per_step = timedelta_to_days(self.model.timedelta_per_step())

            if atmosphere.carbon_dioxide > self.get_agent_type_attribute("max_carbon_pressure_trigger"):
                co2_lost = days_per_step * self.get_agent_type_attribute("carbon_per_hour")
                atmosphere.modify_carbon_dioxide_by_mass(-1 * co2_lost)
