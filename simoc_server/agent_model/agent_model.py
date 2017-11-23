from .astronaut import AstronautAgent
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

class AgentModel(object):

	def __init__(self, grid_width, grid_height):
		self.grid_width = grid_width
		self.grid_height = grid_height
		self.grid = MultiGrid(self.grid_width, self.grid_height)
		self.scheduler = RandomActivation(self)
		print("done")
