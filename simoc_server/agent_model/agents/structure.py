from simoc_server.agent_model.agents.core import BaseAgent
from simoc_server.agent_model.agents.plants import PlantAgent
from simoc_server.exceptions import AgentModelError


class PlumbingSystem(BaseAgent):
    _agent_type_name = "plumbing_system"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attr("water", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("waste_water", 0.0, is_client_attr=True, is_persisted_attr=True)

class Atmosphere(BaseAgent):
    _agent_type_name = "atmosphere"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attr("temp", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("volume", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("oxygen", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("carbon_dioxide", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("nitrogen", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("argon", 0.0, is_client_attr=True, is_persisted_attr=True)


    def change_volume(self, volume_delta, maintain_pressure=False):
        new_volume = self.volume + volume_delta

        if new_volume < 0:
            raise AgentModelError("Attempted to subtract more volume from available amount.")

        if not maintain_pressure:
            # p1v1 = p2v2 -> p2 = p1v1/v2
            p2 = (self.pressure * self.volume) / new_volume

            ratio = p2/self.pressure

            self.oxygen *= ratio
            self.carbon_dioxide *= ratio
            self.nitrogen *= ratio
            self.argon *= ratio

        self.volume = new_volume


class Structure(BaseAgent):

    _agent_type_name = "default_structure"
    #TODO: Implement structure sprites

    def __init__(self, *args, **kwargs):
        plumbing_system = kwargs.pop("plumbing_system", None)
        atmosphere = kwargs.pop("atmosphere", None)

        super().__init__(*args, **kwargs)

        self._attr("plumbing_system", None, _type=Atmosphere, is_client_attr=True, is_persisted_attr=True)
        self._attr("atmosphere", None, _type=Atmosphere, is_client_attr=True, is_persisted_attr=True)

        self._attr("width", self.get_agent_type_attribute("width"), is_client_attr=True,
            is_persisted_attr=True)
        self._attr("height", self.get_agent_type_attribute("height"), is_client_attr=True,
            is_persisted_attr=True)
        self._attr("length", self.get_agent_type_attribute("length"), is_client_attr=True,
            is_persisted_attr=True)

        self.agents = []

    @property
    def volume(self):
        return self.width * self.height * self.length

    def set_atmosphere(self, atmosphere, maintain_pressure=False):
        self.atmosphere = atmosphere
        self.atmosphere.change_volume(self.volume,
            maintain_pressure=maintain_pressure)

    def set_plumbing_system(self, plumbing_system):
        # use function for later operations that may be applied
        # when adding a plumbing system
        self.plumbing_system = plumbing_system

    def place_agent_inside(self, agent):
        self.agents.append(agent)

    def remove_agent_from(self, agent):
        self.agents.remove(agent)


# Structure sub-agents

#Enter description here
class Airlock(Structure):

    _agent_type_name = "airlock"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def step(self):
        pass


#Human agents resting inside will get energy back
class CrewQuarters(Structure):

    _agent_type_name = "crew_quarters"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.needed_agents = ['Water_Reclaimer','CO2_Scrubber']

    def step(self):
        pass


#Grows plant agents using agricultural agents
class Greenhouse(Structure):

    _agent_type_name = "greenhouse"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.needed_agents = ['Planter','Hydroponics','Composter','Harvestor','Processor']
    def step(self):
        pass
    def check_agents(self):
        pass


#Converts plant mass to food
#Input: Plant Mass
#Output: Edible and Inedible Biomass
class Kitchen(Structure):

    _agent_type_name = "kitchen"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def step(self):
        #if(plantmass >= increment)
        #    plantmass -= increment
        #   ediblemass += (efficiency * increment)
        #    inediblemass += (increment - (efficiency * increment))
        pass


#Generates power (assume 100% for now)
#Input: Solar Gain, 1/3 Power gain of Earth
#Output: 100kW Energy
class PowerStation(Structure):

    _agent_type_name = "power_station"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power_output = 100
    def step(self):
        pass


#A place for rockets to land and launch
class RocketPad(Structure):

    _agent_type_name = "rocket_pad"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def step(self):
        pass


#A place for the rover to seal to the habitat
class RoverDock(Structure):

    _agent_type_name = "rover_dock"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def step(self):
        pass


#Storage for raw materials and finished goods
class StorageFacility(Structure):

    _agent_type_name = "storage_facility"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage_capacity = 1000
    def step(self):
        pass