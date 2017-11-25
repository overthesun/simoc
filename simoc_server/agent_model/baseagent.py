from abc import ABCMeta, abstractmethod
from mesa import Agent
from simoc_server.database.db_model import AgentType, AgentEntity, AgentAttribute
from simoc_server import db
from uuid import uuid4

PERSISTABLE_ATTRIBUTE_TYPES = [int.__name__, float.__name__, str.__name__, type(None).__name__]

class BaseAgent(Agent):
    __metaclass__ = ABCMeta

    __agent_type_name__ = None
    __agent_type_attributes_loaded__ = False

    def __init__(self, model, agent_entity=None):
        self.type = self.__class__.__name__
        self.load_agent_type_attributes()
        #self.sprite_mapper = DefaultSpriteMapper
        if agent_entity is not None:
            self.load_from_db(agent_entity)
        else:
            unique_id = "{0}_{1}".format(self.__class__.__name__, uuid4())
            self.persisted_attributes = set()
            self.client_attributes = set()
            self.init_new()
            agent_entity = self.create_entity(model, unique_id)

        self.agent_entity = agent_entity
        unique_id = self.agent_entity.agent_unique_id
        super().__init__(unique_id, model)

    @abstractmethod
    def init_new(self):
        raise NotImplemented("Must implement in derived class")


    def load_agent_type_attributes(self):
        if not self.__class__.__agent_type_name__:
            raise Exception("__agent_type_name__ not set")
        if not self.__class__.__agent_type_attributes_loaded__:
            agent_type_name = self.__class__.__agent_type_name__
            agent_type = AgentType.query.filter_by(name=agent_type_name).first()
            self.__class__.agent_type_attributes = {}
            self.__class__._load_database_attributes_into(agent_type.agent_type_attributes,
                self.__class__.agent_type_attributes)
            __agent_type_attributes_loaded__ = True
            self.__class__.__agent_type__ = agent_type

    def get_agent_type_attribute(self, name):
        return self.__class__.agent_type_attributes[name]

    def load_from_db(self, agent_entity):
        self.pos = (agent_entity.pos_x, agent_entity.pos_y)
        self.unique_id = agent_entity.agent_unique_id
        self.__class__._load_database_attributes_into(agent_entity.agent_attributes,
            self.__dict__)

    @classmethod
    def _load_database_attributes_into(cls, attributes, target):
        for attribute in attributes:
            # get type of attribute
            if attribute.value_type == type(None).__name__:
                value = None
            else:
                value_type = eval(attribute.value_type)
                value_str = attribute.value
                value = value_type(value_str)
            attribute_name = attribute.name
            target[attribute_name] = value

    def create_entity(self, model, unique_id):
        agent_entity = AgentEntity(agent_type=self.__class__.__agent_type__,
                 agent_model_entity=model.agent_model_entity, agent_unique_id=unique_id)
        for attribute_name in self.persisted_attributes:
            value_str, value_type = self._get_instance_attribute_params(attribute_name)
            agent_entity.agent_attributes.append(AgentAttribute(name=attribute_name, 
                value=value_str, value_type=value_type))
        return agent_entity

    def _get_instance_attribute_params(self, attribute_name):
        value = self.__dict__[attribute_name]
        value_type = type(value).__name__
        value_str = str(value)
        if value_type not in PERSISTABLE_ATTRIBUTE_TYPES:
            raise Exception("Attribute set to non-persistable type.")
        return value_str, value_type

    def register_persisted_attribute(self, attribute_name):
        self.persisted_attributes.add(attribute_name)

    def register_client_attribute(self, attribute_name):
        self.client_attributes.add(attribute_name)

    def get_sprite_mapping(self):
        return self.sprite_mapper.get_sprite_mapping(self)

    def save(self, commit=True):
        for agent_attribute in self.agent_entity.agent_attributes:
            value_str, value_type = self._get_instance_attribute_params(agent_attribute.name)
            agent_attribute.value_type = value_type
            agent_attribute.value = value_str
            db.session.add(agent_attribute)
        self.agent_entity.pos_x = self.pos[0]
        self.agent_entity.pos_y = self.pos[1]
        db.session.add(self.agent_entity)
        if commit:
            db.session.commit()