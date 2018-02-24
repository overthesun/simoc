from simoc_server.agent_model.agents.core import EnclosedAgent

class Planter(EnclosedAgent):
	agent_type_name = "planter"
	# TODO right now just grows generic plant, the planter should choose a specific type somehow
	# TODO planter plants everything in one step, should be incremental
	# TODO planter should use soil
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		my_greenhouse = self.structure

	def step(self):
		if(my_greenhouse.plants_housed < my_greenhouse.max_plants):
			to_plant = my_greenhouse.max_plants - my_greenhouse.plants_housed
			self.plant(to_plant) 

	def plant(self, number_to_plant):
		for x in range(0, number_to_plant):
			plant_agent = agents.PlantAgent(self.model, structure=my_greenhouse)
			self.model.add_agent(plant_agent)
			my_greenhouse.place_plant_inside(plant_agent)