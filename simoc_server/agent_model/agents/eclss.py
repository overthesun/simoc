from simoc_server.agent_model.agents.core import EnclosedAgent
from simoc_server.util import timedelta_to_days

class CarbonScrubber(EnclosedAgent):
    _agent_type_name = "carbon_scrubber"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def step(self):
        atmosphere = self.structure.atmosphere

        days_per_step = timedelta_to_days(self.model.timedelta_per_step())
        if atmosphere.carbon_dioxide > self.get_agent_type_attribute("max_carbon_pressure_trigger"):
            co2_lost = days_per_step * self.get_agent_type_attribute("carbon_per_hour")
            atmosphere.modify_carbon_dioxide_by_mass(-1 * co2_lost)
