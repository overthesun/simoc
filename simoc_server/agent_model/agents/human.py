import math
import datetime

from simoc_server.agent_model import agents, agent_model_util
from simoc_server.agent_model.agents.core import EnclosedAgent
from simoc_server.util import timedelta_to_days, timedelta_hour_of_day
from simoc_server.exceptions import AgentModelError

HUMAN_DEATH_REASONS = {
    "no_atmosphere": "No Atmosphere",
    "low_o2":"Insufficient oxygen.",
    "high_co2":"Excess CO2",
    "dehydrated":"Dehydration",
    "starved":"Starvation"
}

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
        self._attr("days_without_water", 0.0, is_client_attr=True, is_persisted_attr=True)

    def step(self):
        if self.structure is None:
            raise AgentModelError("Enclosing structure was not set for human agent.")

        timedelta_per_step = self.model.timedelta_per_step()
        hour_of_day = timedelta_hour_of_day(self.model.model_time)
        days_per_step = timedelta_to_days(timedelta_per_step)
        atmosphere = self.structure.atmosphere
        plumbing_system = self.structure.plumbing_system

        if atmosphere is None:
            self.kill(HUMAN_DEATH_REASONS["no_atmosphere"])
        elif atmosphere.oxygen < self.get_agent_type_attribute("fatal_o2_lower"):
            self.kill(HUMAN_DEATH_REASONS["low_o2"])
        elif atmosphere.carbon_dioxide > self.get_agent_type_attribute("fatal_co2_upper"):
            self.kill(HUMAN_DEATH_REASONS["high_co2"])
        elif self.days_without_water > self.get_agent_type_attribute("max_dehydration_days"):
            self.kill(HUMAN_DEATH_REASONS["dehydrated"])
        elif self.energy <= 0:
            self.kill(HUMAN_DEATH_REASONS["starved"])
        else:
            # TODO decide what kitches are available to human if seperated colonys exist
            kitchens = self.model.get_agents(agents.Kitchen)
            consumed_energy = 0
            for kitchen in kitchens:
                required_food_energy = self.get_agent_type_attribute("required_food_energy") * days_per_step
                consumed_energy = kitchen.cook_meal(required_food_energy)
                if consumed_energy >= self.get_agent_type_attribute("required_food_energy"):
                    break

            self.energy += consumed_energy
            self.energy = min(self.get_agent_type_attribute("max_energy"), self.energy)

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

            moles_oxygen_output = 0
            moles_oxygen_input = 0
            waste_water_added = 0
            # TODO intelligent water usage
            if total_water_usage <= plumbing_system.water and plumbing_system is not None:
                self.days_without_water = 0.0

                grey_water = self.get_agent_type_attribute("grey_water_output") * days_per_step
                grey_water_solids = self.get_agent_type_attribute("grey_water_solid_output") * days_per_step
                solid_waste = self.get_agent_type_attribute("solid_waste_output") * days_per_step
                waste_water = total_waste_water_output * days_per_step

                plumbing_system.water -= total_water_usage
                plumbing_system.grey_water += grey_water
                plumbing_system.waste_water += waste_water
                plumbing_system.grey_water_solids += grey_water_solids
                plumbing_system.solid_waste += solid_waste

                waste_water_added += waste_water
                moles_oxygen_input += agent_model_util.mass_water_to_moles(total_water_usage)
                moles_oxygen_output += agent_model_util.mass_water_to_moles(grey_water)
                moles_oxygen_output += agent_model_util.mass_water_to_moles(waste_water)
                # TODO temporary fix, violates conservation of mass, this is fixed
                # at the end as a temporary solution
                if plumbing_system.water < 0:
                    self.plumbing_system.water = 0
            else:
                # TODO determine metabolic waste water to output in a dehydration scenario
                # if this is conserved by the body, it will need to be expelled later
                # to stay in the model
                self.days_without_water += days_per_step


            oxygen_input = self.get_agent_type_attribute("oxygen_consumption") * days_per_step
            carbon_output = self.get_agent_type_attribute("carbon_produced") * days_per_step

            actual_oxygen_in, actual_carbon_out = atmosphere.convert_o2_to_co2(oxygen_input, carbon_output, 
                self.get_agent_type_attribute("fatal_o2_lower"))


            if actual_oxygen_in < oxygen_input:
                # Intermediate check to see if we ran out
                # of oxygen
                self.kill(HUMAN_DEATH_REASONS["low_o2"])

            # multiply both values by 2 since there are 2 oxygen molecules
            moles_oxygen_input += agent_model_util.mass_o2_to_moles(actual_oxygen_in) * 2
            moles_oxygen_output += agent_model_util.mass_co2_to_moles(actual_carbon_out) * 2

            # Temporary solution to prevent loss of oxygen atoms
            if moles_oxygen_input > moles_oxygen_output:
                # if we input more than we output add to waste water
                # this could happen if we had no more water and
                # did not calculate output waste water, it also
                # appears to happen under normal conditions to some extent
                # right now
                moles_diff = moles_oxygen_input - moles_oxygen_output
                plumbing_system.waste_water += agent_model_util.moles_water_to_mass(moles_diff)
            elif moles_oxygen_input < moles_oxygen_output:
                # if we output more then we took in, first take it back from the waste
                # water, then take it back from the co2 this could happen
                # if we went negative for water input and set it back to 0
                moles_diff = moles_oxygen_output - moles_oxygen_input
                diff_water_mass = agent_model_util.moles_water_to_mass(moles_diff)
                if waste_water_added > 0:
                    removed_waste_water = min(waste_water_added, diff_water_mass)
                    moles_diff -= agent_model_util.mass_water_to_moles(removed_waste_water)
                    plumbing_system.waste_water -= removed_waste_water
                if moles_diff > 0:
                    atmosphere.modify_carbon_dioxide_by_mass(agent_model_util.moles_co2_to_mass(moles_diff / 2))

    def kill(self, reason):
        self.model.logger.info("Human Died! Reason: {}".format(reason))
        self.cause_of_death = reason
        self.destroy()

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

        used_energy = ((A - (age_factor * self.age) + B * ((mass_factor * self.mass) + 
            (height_factor * self.height)))/(C)) * (work_factor * days_per_step) * 1000.0
        self.model.logger.info("Energy usage {}".format(used_energy))
        self.energy -= used_energy

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
