from .baseagent import BaseAgent

class AstronautAgent(BaseAgent):
	sequence_number = 0

	def init_new(self):
		health = 100
		height = 160
		weight = 210

		something_not_for_client = "something"

		self.register_persisted_attribute(health)
		self.register_persisted_attribute(height)
		self.register_persisted_attribute(weight)
		self.register_persisted_attribute(something_not_for_client)
		self.register_client_attribute(height)
		self.register_client_attribute(weight)

		self.sprite_mapper = AstronautSpriteMapper
