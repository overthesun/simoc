from simoc_server.agent_model.agents.core import EnclosedAgent

class Harvester(EnclosedAgent):
	agent_type_name = "harvester"
	# TODO harvester harvests all plants in one step, maybe needs to be incremental
	# TODO add harvested mass to storage
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		my_greenhouse = self.structure

	def step(self):
		if (my_greenhouse.plants_ready > 0):
			self.harvest()

	def harvest(self):
		for x in my_greenhouse.plants:
			if(my_greenhouse.plants[x].status == "grown"):
				edible_mass = my_greenhouse.plants[x].get_agent_type_attribute("edible")
				inedible_mass = my_greenhouse.plants[x].get_agent_type_attribute("inedible")
				self.ship(edible_mass, inedible_mass)
				self.structure.remove_plant(my_greenhouse.plants[x])
				my_greenhouse.plants[x].destroy()
				my_greenhouse.plants_ready -= 1
			if(my_greenhouse.plants_ready == 0):
				break

	def ship(self, edible, inedible):
		# TODO for future iterations, should prioritize storage agents that already contain resource to be stored
		# TODO overflow mass is flag to create new storage
		possible_storage = self.model.get_agents("storage_facility")
		edible_to_store = edible
		inedible_to_store = inedible
		for x in possible_storage:
			if(edible_to_store > 0):
				edible_to_store -= possible_storage[x].store("edible_mass", edible)
			if(inedible_to_store > 0):
				inedible_to_store -= possible_storage[x].store("inedible_mass", inedible)
			if(edible_to_store == 0 and inedible_to_store == 0):
				break
			
