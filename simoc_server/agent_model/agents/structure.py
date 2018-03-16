from collections import OrderedDict

from simoc_server.agent_model import agent_model_util
from simoc_server.agent_model.agents.core import BaseAgent
from simoc_server.agent_model.agents.plants import PlantAgent
from simoc_server.agent_model.agents.core import EnclosedAgent
from simoc_server.agent_model import agents
from simoc_server.exceptions import AgentModelError
from simoc_server.util import timedelta_to_days


class PlumbingSystem(BaseAgent):
    _agent_type_name = "plumbing_system"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # All values in kgs

        # 'drinkable water' in the water system
        self._attr("water", 0.0, is_client_attr=True, is_persisted_attr=True)
        # 'waste water' in the waste water system (contains solid waste)
        self._attr("waste_water", 0.0, is_client_attr=True, is_persisted_attr=True)
        # 'grey water' in the grey water system
        self._attr("grey_water", 0.0, is_client_attr=True, is_persisted_attr=True)

        # solids in the 'grey water' system
        self._attr("grey_water_solids", 0.0, is_client_attr=True, is_persisted_attr=True)
        # solids in the 'waste water' system
        self._attr("solid_waste", 0.0, is_client_attr=True, is_persisted_attr=True)

    def water_to_waste_water(self, amount):
        self.water -= amount
        self.waste_water += amount

    def waste_water_to_water(self, amount):
        self.waste_water -= amount
        self.water += amount

    def grey_water_to_water(self, amount):
        self.grey_water -= amount
        self.water += amount

    def water_to_gray_water(self, amount):
        self.water -= amount
        self.grey_water += amount

    def grey_water_to_waste_water(self, amount):
        self.grey_water -= amount
        self.waste_water += amount

class Atmosphere(BaseAgent):
    _agent_type_name = "atmosphere"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # All gas values stored as pressures measured in kPa

        self._attr("temp", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("volume", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("oxygen", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("carbon_dioxide", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("nitrogen", 0.0, is_client_attr=True, is_persisted_attr=True)
        self._attr("argon", 0.0, is_client_attr=True, is_persisted_attr=True)

    @property
    def total_pressure(self):
        return self.oxygen + self.carbon_dioxide + self.nitrogen + self.argon

    @property
    def total_moles(self):
        # n = (PV)/(RT)
        return agent_model_util.moles_of_gas(self.total_pressure, self.volume, self.temp)

    @property
    def moles_oxygen(self):
        return agent_model_util.moles_of_gas(self.oxygen, self.volume, self.temp)

    @property
    def moles_carbon_dioxide(self):
        return agent_model_util.moles_of_gas(self.carbon_dioxide, self.volume, self.temp)

    @property
    def moles_nitrogen(self):
        return agent_model_util.moles_of_gas(self.nitrogen, self.volume, self.temp)

    @property
    def moles_argon(self):
        return agent_model_util.moles_of_gas(self.argon, self.volume, self.temp)

    def change_temp(self, temp_delta, maintain_pressure=False):
        new_temp = self.temp + temp_delta

        if not maintain_pressure:
            # PV = nRT
            # P1/T1 = P2/T2
            # P2 = (P1T1)/T2

            p2 = (self.total_pressure * self.temp) / float(new_temp)

            ratio = p2/self.pressure

            self.oxygen *= ratio
            self.carbon_dioxide *= ratio
            self.nitrogen *= ratio
            self.argon *= ratio

        self.temp = new_temp


    def change_volume(self, volume_delta, maintain_pressure=False):
        new_volume = self.volume + volume_delta

        if new_volume < 0:
            raise AgentModelError("Attempted to subtract more volume from available amount.")

        if not maintain_pressure:
            # p1v1 = p2v2 -> p2 = p1v1/v2
            p2 = (self.pressure * self.volume) / float(new_volume)

            ratio = p2/self.pressure

            self.oxygen *= ratio
            self.carbon_dioxide *= ratio
            self.nitrogen *= ratio
            self.argon *= ratio

        self.volume = new_volume

    def convert_o2_to_co2(self, mass_o2_in, mass_co2_out, min_o2_pressure=0.0):
        """Convert o2 to co2 at known ratio

        Parameters
        ----------
        mass_o2_in : float
            Mass of o2 in kilograms to convert to co2
        mass_co2_out : float
            Mass of co2 in kilograms to create from reaction
        min_o2_pressure : float, optional
            Minimum pressure needed to conduct reaction, if o2 pressure
            drops below this value, the reaction will be done partially
            up till this value

        Returns
        -------
        tuple containing
            actual_o2_mass_in float
                the actual mass of o2 in limited by the minimum o2 pressure
            actual_co2_mass_out float
                the actual mass of co2 out limited by the minimum o2 pressure

        Raises
        ------
        AgentModelError
            If min_o2_pressure is negative

        """
        if min_o2_pressure < 0:
            raise AgentModelError("Minimum o2 level cannot be below 0.")

        expected_o2_pressure_in = agent_model_util.mass_o2_to_pressure(mass_o2_in, self.temp, self.volume)
        expected_co2_pressure_out = agent_model_util.mass_co2_to_pressure(mass_co2_out, self.temp, self.volume)

        if self.oxygen - expected_o2_pressure_in < min_o2_pressure:
            # partial breath
            actual_o2_pressure_in = max(0, self.oxygen - min_o2_pressure)
            ratio = actual_o2_pressure_in/expected_o2_pressure_in
            actual_co2_pressure_out = expected_co2_pressure_out * ratio
        else:
            actual_o2_pressure_in = expected_o2_pressure_in
            actual_co2_pressure_out = expected_co2_pressure_out

        self.oxygen -= actual_o2_pressure_in
        self.carbon_dioxide += actual_co2_pressure_out

        actual_o2_mass_in = (actual_o2_pressure_in / expected_o2_pressure_in) * mass_o2_in
        actual_co2_mass_out = (actual_co2_pressure_out / expected_co2_pressure_out) * mass_co2_out
        return actual_o2_mass_in, actual_co2_mass_out

    def convert_co2_to_o2(self, mass_co2_in, mass_o2_out, min_co2_pressure=0.0):
        """Convert co2 to o2 at known ratio

        Parameters
        ----------
        mass_co2_in : float
            Mass of co2 in kilograms to convert to o2
        mass_o2_out : float
            Mass of o2 in kilograms to create from reaction
        min_co2_pressure : float, optional
            Minimum pressure needed to conduct reaction, if co2 pressure
            drops below this value, the reaction will be done partially
            up till this value

        Returns
        -------
        tuple containing
            actual_co2_mass_in float
                the actual mass of co2 in limited by the minimum co2 pressure
            actual_o2_mass_out float
                the actual mass of o2 out limited by the minimum co2 pressure

        Raises
        ------
        AgentModelError
            If min_co2_pressure is negative

        """
        if min_co2_pressure < 0:
            raise AgentModelError("Minimum co2 level cannot be below 0.")

        expected_co2_pressure_in = agent_model_util.mass_co2_to_pressure(mass_co2_in, self.temp, self.volume)
        expected_o2_pressure_out = agent_model_util.mass_o2_to_pressure(mass_o2_out, self.temp, self.volume)

        if self.carbon_dioxide - expected_co2_pressure_in < min_co2_pressure:
            # partial breath
            actual_co2_pressure_in = max(0, self.carbon_dioxide - min_co2_pressure)
            ratio = actual_co2_pressure_in/expected_co2_pressure_in
            actual_o2_pressure_out = expected_o2_pressure_out * ratio
        else:
            actual_co2_pressure_in = expected_co2_pressure_in
            actual_o2_pressure_out = expected_o2_pressure_out

        self.carbon_dioxide -= actual_co2_pressure_in
        self.oxygen += actual_o2_pressure_out

        actual_co2_mass_in = (actual_co2_pressure_in / expected_co2_pressure_in) * mass_co2_in
        actual_o2_mass_out = (actual_o2_pressure_out / expected_o2_pressure_out) * mass_o2_out
        return actual_co2_mass_in, actual_o2_mass_out

    def modify_oxygen_by_mass(self, mass_kg):
        """Change the oxygen pressure by the given delta of oxygen in kgs

        Parameters
        ----------
        mass_kg : float
            Mass of oxygen to modify atmosphere by
        """
        self.oxygen += agent_model_util.mass_o2_to_pressure(mass_kg, self.temp, self.volume)

    def modify_carbon_dioxide_by_mass(self, mass_kg):
        """Change the co2 pressure by the given delta of co2 in kgs

        Parameters
        ----------
        mass_kg : float
            Mass of co2 to modify atmosphere by
        """
        self.carbon_dioxide += agent_model_util.mass_co2_to_pressure(mass_kg, self.temp, self.volume)

    def modify_nitrogen_by_mass(self, mass_kg):
        """Change the nitrogen pressure by the given delta of nitrogen in kgs

        Parameters
        ----------
        mass_kg : float
            Mass of nitrogen to modify atmosphere by
        """
        self.nitrogen += agent_model_util.mass_nitrogen_to_pressure(mass_kg)

    def modify_argon_by_mass(self, mass_kg):
        """Change the argon pressure by the given delta of argon in kgs

        Parameters
        ----------
        mass_kg : float
            Mass of argon to modify atmosphere by
        """
        self.argon += agent_model_util.mass_argon_to_pressure(mass_kg)



class Structure(BaseAgent):

    _agent_type_name = "default_structure"
    #TODO: Implement structure sprites

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attr("plumbing_system", None, _type=PlumbingSystem, is_client_attr=True, is_persisted_attr=True)
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
        if(agent in self.agents):
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
        self.plants = []

    def step(self):
        pass

    def place_agent_inside(self, agent):
        super().place_agent_inside(agent)
        if isinstance(agent, agents.PlantAgent):
            self.plants.append(agent)

    def remove_agent_from(self, agent):
        super().remove_agent_from(agent)
        if(agent in self.plants):
            self.plants.remove(agent)


#Harvester 

class Harvester(EnclosedAgent):
    agent_type_name = "harvester"
    # TODO harvester harvests all plants in one step, maybe needs to be incremental
    # Plant matter densities
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def step(self):
        plants_ready = []
        for x in self.structure.plants:
            if(x.is_grown()):
                plants_ready.append(x)
        self.harvest(plants_ready)

    def harvest(self, plants):
        for x in plants:
            plant_age = timedelta_to_days(x.age)
            mature_age = timedelta_to_days(x.growth_period)

            # limit growth to maturity age
            maturity_coefficient = max(plant_age, mature_age)
            edible_mass = x.get_agent_type_attribute("edible") * maturity_coefficient
            inedible_mass = x.get_agent_type_attribute("inedible") * maturity_coefficient
            plant_density = x.get_agent_type_attribute("density")
            energy_density = x.get_agent_type_attribute("energy_density")
            #Needs different densities for inedible/edible, add to plant attr
            self.ship(edible_mass, inedible_mass, plant_density, energy_density)
            x.destroy()

    def ship(self, edible, inedible, plant_density, energy_density):
        possible_storage = self.model.get_agents(StorageFacility)
        edible_to_store = edible
        inedible_to_store = inedible

        for x in possible_storage:
            stored_food_unit = x.get_stored_food()
            inedible_mass_unit = x.get_inedible_mass()
            if(edible_to_store > 0):
                stored_energy, stored_mass = stored_food_unit.accumulate(edible, plant_density, energy_density)
                edible_to_store -= stored_mass
            if(inedible_to_store > 0):
                stored_mass = inedible_mass_unit.accumulate(inedible, plant_density)
                inedible_to_store -= stored_mass
            if(edible_to_store == 0 and inedible_to_store == 0):
                break

#Planter

class Planter(EnclosedAgent):
    _agent_type_name = "planter"
    # TODO planter plants everything in one step, should be incremental
    # TODO planter should use soil
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def step(self):
        self.plant()

    def plant(self):
        current_plants = self.structure.plants

        # make copy of the plants_available, maintaining order
        # to ensure consistent execution of the model
        # when using the same random seed
        needed_plants = OrderedDict(self.model.plants_available)

        for plant in current_plants:
            try:
                needed_plants[plant._agent_type_name] -= 1
            except KeyError:
                pass

        random_state = self.model.random_state

        needed_plant_names = list(needed_plants.keys())
        random_state.shuffle(needed_plant_names)

        for plant_name in needed_plant_names:
            num_needed = needed_plants[plant_name]
            for i in range(num_needed):
                if len(self.structure.plants) >= self.structure.get_agent_type_attribute("max_plants"):
                    break
                plant_agent_class = agents.get_agent_by_type_name(plant_name)
                plant_agent = plant_agent_class(self.model, structure=self.structure)
                self.model.add_agent(plant_agent)

#Converts plant mass to energy
#Input: Edible Plant Mass
#Output: Energy
class Kitchen(EnclosedAgent):

    _agent_type_name = "kitchen"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def step(self):
        pass

    def cook_meal(self, energy):
        storage = self.model.get_agents(StorageFacility)

        needed_energy = energy
        actual_energy = 0
        for x in storage:
            stored_food_unit = x.get_stored_food()
            energy_delta, supplied_mass = stored_food_unit.supply_energy(needed_energy)
            needed_energy -= energy_delta
            actual_energy += energy_delta
        return actual_energy


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

class StoredMass(EnclosedAgent):
    _agent_type_name = "stored_mass"

    def __init__(self, *args, **kwargs):
        volume = float(kwargs.pop("volume", 0.0))
        mass = float(kwargs.pop("mass", 0.0))

        structure = getattr(kwargs, "structure", None)
        if structure is not None and not isinstance(structure, StorageFacility):
            raise AgentModelError("StoredMass must be stored in StorageFacility")

        super().__init__(*args, **kwargs)

        self._attr("volume", default_value=volume, is_client_attr=True, is_persisted_attr=True)
        self._attr("mass", default_value=mass, is_client_attr=True, is_persisted_attr=True)

    @property
    def current_density(self):
        if self.volume > 0:
            return self.mass/self.volume
        else:
            return float('nan')

    def accumulate(self, mass_kg, density):
        requested_volume = mass_kg / density
        actual_volume = self.structure.store_volume(requested_volume)
        actual_mass = actual_volume * density

        self.volume += actual_volume
        self.mass += actual_mass

        return actual_mass

    def supply_mass(self, requested_mass):
        actual_mass = 0
        if self.mass > 0:
            actual_mass = min(requested_mass, self.mass)

            # get density before changing volume
            density = self.current_density

            self.mass -= actual_mass

            if self.mass == 0:
                # if all mass is spent, explicitly set
                # volume to 0 to avoid rounding error
                lost_volume = self.volume
            else:
                # calculate volume lost
                lost_volume = actual_mass / density

            self.volume -= lost_volume

            # update storage volume
            self.structure.release_volume(lost_volume)
        return actual_mass

class StoredFood(StoredMass):
    _agent_type_name = "stored_food"

    def __init__(self, *args, **kwargs):
        food_energy = float(kwargs.pop("food_energy", 0.0))

        super().__init__(*args, **kwargs)

        self._attr("food_energy", default_value=food_energy, is_client_attr=True, is_persisted_attr=True)

    @property
    def current_food_energy_density(self):
        """Current food energy density in kJ/kg

        Returns
        -------
        float
            The energy density
        """
        if self.mass > 0:
            return self.food_energy/self.mass
        else:
            return float('nan')

    def accumulate(self, mass_kg, density, energy_density):
        print("mass_kg: {} density: {} energy_density: {}".format(mass_kg, density, energy_density))
        actual_mass = super().accumulate(mass_kg, density)
        actual_energy = actual_mass * energy_density
        self.food_energy += actual_energy
        print("actual mass: {} actual_energy: {}".format(actual_mass, actual_energy))
        return actual_mass, actual_energy

    def supply_mass(self, requested_mass, return_energy=False):
        actual_mass = 0
        energy_lost = 0

        if self.mass > 0:
            # get food energy density before changing mass
            food_energy_density = self.current_food_energy_density

            # modifies mass and volume
            actual_mass = super().supply_mass(requested_mass)

            if self.mass == 0:
                # if all mass is spent, explicitly
                # set energy lost to avoid rounding error
                energy_lost = self.food_energy
            else:
                # calculate resultant energy loss
                energy_lost = actual_mass * food_energy_density
            # subtract energy lost from total energy
            self.food_energy -= energy_lost

        if return_energy:
            return actual_mass, energy_lost
        else:
            return actual_mass

    def supply_energy(self, requested_energy):
        actual_energy = 0
        actual_mass = 0
        if self.food_energy > 0:
            # calculate the available energy to give
            calculated_energy = min(requested_energy, self.food_energy)

            # calculate the resultant mass
            calculated_mass = calculated_energy / self.current_food_energy_density

            # calculate the actual energy (may be slightly different with rounding error)
            # and actual energy (again rounding error may change this value slightly)
            actual_mass, actual_energy = self.supply_mass(calculated_mass, return_energy=True)

        return actual_energy, actual_mass


# class StoredItem(EnclosedAgent):
#     # Potential implementation of Stored item for later Use
#     _agent_type_name = "stored_item"

#     def __init__(self, *args, **kwargs):
#         volume_per_item = float(kwargs.pop("volume_per_item", 0.0))
#         mass_per_item = float(kwargs.pop("mass_per_item", 0.0))
#         count = int(kwargs.pop("count", 0))

#         super().__init__(*args, **kwargs)

#         self._attr("volume_per_item", default_value=volume_per_item, is_client_attr=True, is_persisted_attr=True)
#         self._attr("mass_per_item", default_value=mass_per_item, is_client_attr=True, is_persisted_attr=True)
#         self._attr("count", default_value=count, is_client_attr=True, is_persisted_attr=True)

#     @property
#     def volume(self):
#         return self.volume_per_item * self.count

#     @property
#     def mass(self):
#         return self.mass_per_item * self.count

#Storage for raw materials and finished goods
class StorageFacility(Structure, EnclosedAgent):

    _agent_type_name = "storage_facility"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "structure" in kwargs:
            self.set_capacity()

    def post_db_load(self):
        super().post_db_load()
        self.set_capacity()

    def set_capacity(self):
        if self.structure:
            self.storage_capacity = self.structure.volume

    def step(self):
        pass

    def store_volume(self, requested_volume):
        print("in: {}".format(requested_volume))
        storable = min(requested_volume, self.storage_capacity)
        self.storage_capacity += storable
        print("actual in: {}".format(storable))
        return storable

    def release_volume(self, requested_volume):
        print("out: {}".format(requested_volume))
        new_capacity = self.storage_capacity - requested_volume

        if new_capacity < 0:
            raise AgentModelError("Requested release of more volume than is available.")

        self.storage_capacity = new_capacity

    def get_or_create(self, resource_name, agent_class, *args, **kwargs):
        kwargs["structure"] = self
        resource = getattr(self, resource_name, None)
        if not resource:
            resource = agent_class(self.model, *args, **kwargs)
            self.model.add_agent(resource)
            self._attr(resource_name, resource, is_client_attr=True, is_persisted_attr=True)
        return resource

    def get_stored_food(self):
        return self.get_or_create("stored_food", StoredFood)

    def get_inedible_mass(self):
        return self.get_or_create("inedible_mass", StoredMass)