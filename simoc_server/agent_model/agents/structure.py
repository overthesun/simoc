import datetime

from simoc_server.agent_model.agents.core import BaseAgent
from simoc_server.agent_model.agents.plants import PlantAgent
from simoc_server.agent_model.agents.core import EnclosedAgent
from simoc_server.agent_model import agents
from simoc_server.exceptions import AgentModelError
from simoc_server.util import to_volume, timedelta_to_days


class PlumbingSystem(BaseAgent):
    _agent_type_name = "plumbing_system"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attr("water", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("waste_water", 0.0, is_client_attr=True, is_persisted_attr=True)

    def water_to_waste(self, amount):
        self.water -= amount
        self.waste_water += amount

    def waste_to_water(self, amount):
        self.waste_water -= amount
        self.water += amount

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
        self.needed_agents = ['Planter','Harvester']
        self._attr("plants_ready", 0,is_client_attr=True, is_persisted_attr=True)
        self._attr("max_plants", 50,is_client_attr=True, is_persisted_attr=True)
        self.plants = []

    def step(self):
        pass

    def place_plant_inside(self, agent):
        self.plants.append(agent)

    def remove_plant(self, agent):
        self.plants.remove(agent)

#Harvester 

class Harvester(EnclosedAgent):
    agent_type_name = "harvester"
    # TODO harvester harvests all plants in one step, maybe needs to be incremental
    # Plant matter densities
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plant_mass_density = 721 #NOT ACTUAL DENSITY kg/m^3

    def step(self):
        if (self.structure.plants_ready > 0):
            self.harvest()

    def harvest(self):
        for x in self.structure.plants:
            if(x.status == "grown"):
                plant_age = timedelta_to_days(self.model.model_time - x.model_time_created)
                edible_mass = x.get_agent_type_attribute("edible") * plant_age
                inedible_mass = x.get_agent_type_attribute("inedible") * plant_age
                #Needs different densities for inedible/edible, add to plant attr
                self.ship(to_volume(edible_mass, self.plant_mass_density), to_volume(inedible_mass, self.plant_mass_density))
                self.structure.remove_plant(x)
                x.destroy()
                self.structure.plants_ready -= 1
            if(self.structure.plants_ready == 0):
                break

    def ship(self, edible, inedible):
        possible_storage = self.model.get_agents(StorageFacility)
        edible_to_store = edible
        inedible_to_store = inedible
        for x in possible_storage:
            if(edible_to_store > 0):
                edible_to_store -= x.store("edible_mass", edible)
            if(inedible_to_store > 0):
                inedible_to_store -= x.store("inedible_mass", inedible)
            if(edible_to_store == 0 and inedible_to_store == 0):
                break

#Planter

class Planter(EnclosedAgent):
    agent_type_name = "planter"
    # TODO right now just grows generic plant, the planter should choose a specific type somehow
    # TODO planter plants everything in one step, should be incremental
    # TODO planter should use soil
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def step(self):
        #FOR TESTING print(self.structure.plants_housed)
        #FOR TESTING print(self.structure.max_plants)

        if(len(self.structure.plants) < self.structure.max_plants):
            to_plant = self.structure.max_plants - len(self.structure.plants)
            self.plant(to_plant) 

        #FOR TESTING print(self.structure.plants[0].status)

    def plant(self, number_to_plant):
        for x in range(0, number_to_plant):
            plant_agent = agents.PlantAgent(self.model, structure=self.structure)
            self.model.add_agent(plant_agent)
            self.structure.place_agent_inside(plant_agent)
            self.structure.place_plant_inside(plant_agent)             

#Converts plant mass to food
#Input: Plant Mass
#Output: Edible and Inedible Biomass
class Kitchen(EnclosedAgent):

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
class StorageFacility(EnclosedAgent):

    _agent_type_name = "storage_facility"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.storage_capacity = self.structure.volume

    def step(self):
        pass

    def store(self, resource, quantity):
        amount_stored = quantity

        if(self.storage_capacity == 0):
            amount_stored = 0
            return amount_stored

        if(self.storage_capacity < quantity):
            amount_stored = self.storage_capacity

        if hasattr(self, resource):
            temp = getattr(self, resource) + amount_stored
            setattr(self, resource, temp)
            self.storage_capacity -= amount_stored
        else:
            self._attr(resource, amount_stored, is_client_attr=True, is_persisted_attr=True)
            self.storage_capacity -= amount_stored

        return amount_stored

    def supply(self, resource, quantity):
        amount_supplied = 0

        if hasattr(self, resource):
            amount_stored = getattr(self, resource)
            if(quantity > amount_stored):
                amount_supplied = quantity - amount_stored
                delattr(self, resource)

                return amount_supplied

            if(quantity < amount_stored):
                amount_supplied = quantity
                temp = getattr(self, resource) - amount_supplied
                setattr(self, resource, temp)

                return amount_supplied

        return amount_supplied
