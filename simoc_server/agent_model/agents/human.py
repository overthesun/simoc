import math
import datetime

from simoc_server.agent_model.agents.core import EnclosedAgent
from simoc_server.util import timedelta_to_days, timedelta_hour_of_day
from simoc_server.exceptions import AgentModelError

# metabolism_work_factor_working
# metabolism_work_factor_idle
# metabolism_C
# metabolism_height_factor
# metabolism_mass_factor
# metabolism_B
# metabolism_age_factor
# metabolism_A
# fatal_co2_upper
# fatal_o2_lower
# medical_water_usage
# hygiene_water_usage
# consumed_water_usage
# max_energy
# max_arrival_age
# min_arrival_age


class HumanAgent(EnclosedAgent):

    _agent_type_name = "human"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO populate std values with non-zero values in database
        mass_mean = self.get_agent_type_attribute("initial_mass_mean")
        mass_std = self.get_agent_type_attribute("initial_mass_std")
        age_mean = self.get_agent_type_attribute("initial_age_mean")
        age_std = self.get_agent_type_attribute("initial_age_std")
        height_mean = self.get_agent_type_attribute("initial_height_mean")
        height_std = self.get_agent_type_attribute("initial_height_std")

        initial_mass = self.model.random_state.normal(mass_mean, mass_std)
        initial_age = self.model.random_state.normal(age_mean, age_std)
        initial_height = self.model.random_state.normal(height_mean, height_std)

        self._attr("energy", self.get_agent_type_attribute("max_energy"), 
            is_client_attr=True, is_persisted_attr=True)

        self._attr("mass", initial_mass,is_client_attr=True, is_persisted_attr=True)
        self._attr("age", initial_age, is_client_attr=True, is_persisted_attr=True)
        self._attr("height", initial_height, is_client_attr=True, is_persisted_attr=True)
        self._attr("days_without_water", default_value=0.0, is_client_attr=True, is_persisted_attr=True)

    def step(self):
        if self.structure is None:
            raise AgentModelError("Enclosing structure was not set for human agent.")

        timedelta_per_step = self.model.timedelta_per_step()
        hour_of_day = timedelta_hour_of_day(self.model.model_time)
        days_per_step = timedelta_to_days(timedelta_per_step)
        atmosphere = self.structure.atmosphere
        plumbing_system = self.structure.plumbing_system

        if(atmosphere is None
            or atmosphere.oxygen < self.get_agent_type_attribute("fatal_o2_lower")
            or atmosphere.carbon_dioxide > self.get_agent_type_attribute("fatal_co2_upper")
            or self.days_without_water > self.get_agent_type_attribute("max_dehydration_days")):

            self.destroy()
        else:
            is_working = hour_of_day < self.get_agent_type_attribute("work_day_hours")
            self._metabolize(is_working, days_per_step)

            # plumbing_system.water_to_waste_water(self._total_water_usage_per_day() * days_per_step)

            # Values based on agent model specification
            # TODO figure out discrepency between water consumption and
            # output, this is likely due to repiration output products
            # including water
            total_waste_water_output = self.get_agent_type_attribute("waste_water_output") + \
                self.get_agent_type_attribute("solid_waste_water_output")

            total_water_usage = self._total_water_usage_per_day() * days_per_step

            # TODO intelligent water usage
            if total_water_usage <= plumbing_system.water and plumbing_system is not None:
                self.days_without_water = 0.0
                plumbing_system.water -= total_water_usage
                plumbing_system.grey_water += self.get_agent_type_attribute("grey_water_output") * days_per_step
                plumbing_system.waste_water += total_waste_water_output * days_per_step
                plumbing_system.grey_water_solids += self.get_agent_type_attribute("grey_water_solid_output") * days_per_step
                plumbing_system.solid_waste += self.get_agent_type_attribute("solid_waste_output") * days_per_step

                # TODO temporary fix, violates conservation of mass
                if plumbing_system.water < 0:
                    self.plumbing_system = 0
            else:
                # TODO determine metabolic waste water to output in a dehydration scenario
                # if this is conserved by the body, it will need to be expelled later
                # to stay in the model
                self.days_without_water += days_per_step


            co2_before = atmosphere.carbon_dioxide
            o2_before = atmosphere.oxygen

            atmosphere.modify_oxygen_by_mass(-1 * self.get_agent_type_attribute("oxygen_consumption") * days_per_step)
            atmosphere.modify_carbon_dioxide_by_mass(self.get_agent_type_attribute("carbon_produced") * days_per_step)

            # TODO temporary fix right here, this violates
            # conservation of matter, and that's bad
            if atmosphere.oxygen < 0:
                atmosphere.oxygen = 0

    def _metabolize(self, is_working, days_per_step):
        # metabolism function from BVAD
        # (A - (age_factor*age(years)) + B(mass_factor*mass(kg) + height_factor*height(m)))/(C * work_factor * time(days))

        if is_working:
            work_factor = self.get_agent_type_attribute("metabolism_work_factor_working")
        else:
            work_factor = self.get_agent_type_attribute("metabolism_work_factor_idle")


        A = self.get_agent_type_attribute("metabolism_A")
        B = self.get_agent_type_attribute("metabolism_B")
        C = self.get_agent_type_attribute("metabolism_C")
        age_factor = self.get_agent_type_attribute("metabolism_age_factor")
        mass_factor = self.get_agent_type_attribute("metabolism_mass_factor")
        height_factor = self.get_agent_type_attribute("metabolism_height_factor")

        self.energy -= ((A - (age_factor * self.age) + B * ((mass_factor * self.mass) + 
            (height_factor * self.height)))/(C)) * (work_factor * days_per_step)

    def _total_water_usage_per_day(self):
        """Calculates the total water usage per day
        from consumed_water, hygiene water, and medical

        If this value is already calculated, return
        cached value

        Returns
        -------
        float
            Total human waste water per day
        """
        try:
            # try cached value
            return self._cached_total_water_usage_per_day
        except AttributeError as ex:
            consumed = self.get_agent_type_attribute("consumed_water_usage")
            hygiene = self.get_agent_type_attribute("hygiene_water_usage")
            medical = self.get_agent_type_attribute("medical_water_usage")

            self._cached_total_water_usage_per_day = consumed + hygiene + medical
            return self._cached_total_water_usage_per_day
