from .baseagent import BaseAgent
from .plants import PlantAgent
from .human import HumanAgent

class Structure(BaseAgent):

	__agent_type_name__ = "default_structure"
	#TODO: Implement structure sprites

	def __init__(self, *args, **kwargs):
		self.agents = []

	def add_agent_to_building(self, agent):
		self.agents.append(agent)


# Structure sub-agents

#Enter description here
class Airlock(Structure):


	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
	def step(self):
		pass


#Human agents resting inside will get energy back
class Crew_Quarters(Structure):


	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.needed_agents = ['Water_Reclaimer','CO2_Scrubber']
	def step(self):
		pass


#Grows plant agents using agricultural agents
class Greenhouse(Structure):


	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.needed_agents = ['Planter','Hydroponics','Composter','Harvestor','Processor']
	def step(self):
		pass
	def check_agents(self):
		pass


#Converts plant mass to food
#Input: Plant Mass
#Output: Edible and Inedible Biomass
class Kitchen(Structure):


	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
	def step(self):
		#if(plantmass >= increment)
		#	plantmass -= increment
		#   ediblemass += (efficiency * increment)
		#	inediblemass += (increment - (efficiency * increment))
		pass


#Generates power (assume 100% for now)
#Input: Solar Gain, 1/3 Power gain of Earth
#Output: 100kW Energy
class Power_Station(Structure):


	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.power_output = 100
	def step(self):
		pass


#A place for rockets to land and launch
class Rocket_Pad(Structure):


	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
	def step(self):
		pass


#A place for the rover to seal to the habitat
class Rover_Dock(Structure):


	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
	def step(self):
		pass


#Storage for raw materials and finished goods
class Storage_Facility(Structure):


	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.storage_capacity = 1000
	def step(self):
		pass