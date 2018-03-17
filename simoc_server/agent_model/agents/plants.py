import datetime

from simoc_server.exceptions import AgentModelError
from simoc_server.util import timedelta_to_days
from simoc_server.agent_model.sprite_mappers import PlantSpriteMapper
from simoc_server.agent_model.agents.core import EnclosedAgent

class PlantAgent(EnclosedAgent):
    # Each plant agent is 1 meter squared worth of that plant
    # TODO possibly parameterize this

    _agent_type_name = "default_plant"
    _sprite_mapper = PlantSpriteMapper

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attr("status", "planted", is_client_attr=True, is_persisted_attr=True)

        # value to track percentage of growth complete, not persisted
        self._attr("growth", default_value=0.0, is_client_attr=True, is_persisted_attr=False)

        self.growth_period = datetime.timedelta(days=self.get_agent_type_attribute("growth_period"))

    @property
    def age(self):
        return self.model.model_time - self.model_time_created
    def step(self):

        if self.structure is None:
            raise AgentModelError("Enclosing structure was not set for plant agent.")

        # TODO determine how long plants can go without water
        water_uptake = self.get_agent_type_attribute("water_uptake")


        atmosphere = self.structure.atmosphere
        plumbing_system = self.structure.plumbing_system

        if atmosphere is None:
            self.kill("No atmosphere.")
        elif plumbing_system is None:
            self.kill("Dehydration (No plumbing system).")
        elif atmosphere.carbon_dioxide < self.get_agent_type_attribute("fatal_co2_lower"):
            self.kill("Insufficient carbon dioxide: {} kpa".format(atmosphere.carbon_dioxide))
        elif water_uptake > plumbing_system.water:
            self.kill("Dehydration (Ran out of water): Water Levels: {} kg.".format(plumbing_system.water))
        elif self.structure.powered == 0:
            print("Greenhouse has no power to grow plant")
        else:
            if not self.is_grown():
                age = self.age
                if age > self.growth_period:
                    self.status = "grown"
                self.growth = min(1.0, age/self.growth_period)

            timedelta_per_step = self.model.timedelta_per_step()
            days_per_step = timedelta_to_days(timedelta_per_step)

            # TODO intake water, currently we have single value
            # which is described as water uptake/transpiration
            # it is unclear how to interpret this value

            # TODO sort out discrepency between o2 and co2
            # consumption/production
            carbon_input = self.get_agent_type_attribute("carbon_uptake") * days_per_step
            oxygen_output = self.get_agent_type_attribute("oxygen_produced") * days_per_step

            actual_carbon_in, actual_oxygen_out = atmosphere.convert_co2_to_o2(carbon_input, oxygen_output, 
                            self.get_agent_type_attribute("fatal_co2_lower"))


    def is_grown(self):
        return self.status == "grown"

    def kill(self, reason):
        self.model.logger.info("Plant Died! Reason: {}".format(reason))
        self.destroy()

class CabbageAgent(PlantAgent):
    _agent_type_name = "cabbage"

class CarrotAgent(PlantAgent):
    _agent_type_name = "carrot"

class ChardAgent(PlantAgent):
    _agent_type_name = "chard"


class DryBeanAgent(PlantAgent):
    _agent_type_name = "dry_bean"

class LettuceAgent(PlantAgent):
    _agent_type_name = "Lettuce"

class PeaAgent(PlantAgent):
    _agent_type_name = "pea"

class PeanutAgent(PlantAgent):
    _agent_type_name = "peanut"

class PepperAgent(PlantAgent):
    _agent_type_name = "pepper"

class RedBeetAgent(PlantAgent):
    _agent_type_name = "red_beet"

class RiceAgent(PlantAgent):
    _agent_type_name = "rice"

class SnapBeanAgent(PlantAgent):
    _agent_type_name = "snap_bean"

class SoybeanAgent(PlantAgent):
    _agent_type_name = "soybean"

class SpinachAgent(PlantAgent):
    _agent_type_name = "spinach"

class StrawberryAgent(PlantAgent):
    _agent_type_name = "strawberry"

class SweetPotatoAgent(PlantAgent):
    _agent_type_name = "sweet_potato"

class TomatoAgent(PlantAgent):
    _agent_type_name = "tomato"

class WheatAgent(PlantAgent):
    _agent_type_name = "wheat"

class WhitePotatoAgent(PlantAgent):
    _agent_type_name = "white_potato"
