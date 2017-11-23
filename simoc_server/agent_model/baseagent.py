from abc import ABCMeta, abstractmethod
from mesa import Agent


class BaseAgent(object):
	__metaclass__ = ABCMeta

	def __init__(self, entity=None):
		self.type = self.__class__.__name__
		self.sprite_mapper = DefaultSpriteMapper
		if entity is not None:
			self.load_from_db(entity)
		else:
			self.persisted_attributes = set()
			self.client_attributes = set()
			self.init_new()
			entity = self.create_entity()

		self.entity = entity

	@abstractmethod
	def init_new(self):
		raise NotImplemented("Must implement in derived class")


	def load_from_db(self):
		self.pos = (self.entity.pos_x, self.entity.pos_y)
		for attribute in self.entity.attributes:
			# get type of attribute
			value_type = eval(attribute.value_type)
			value_str = attribute.value
			self.__dict__[attribute] = value_type(value_str)

	def create_entity(self):
		entity = AgentEntity()
		for attribute_name in self.persisted_attributes:
			value = self.__dict__[attribute_name]
			value_type = type(value)
			if value_type == NoneType:
				raise Exception("None type not allowed for persistent attribute")
			entity.attributes.append(EntityAttribute(name=persisted_attribute, value=value, type=value_type))

	def register_persisted_attribute(self, attribute_name):
		self.persisted_attributes.append(attribute_name)

	def register_client_attribute(self, attribute_name):
		self.client_attributes.append(attribute_name)

	def get_sprite_mapping(self):
		return self.sprite_mapper.get_sprite_mapping(self)