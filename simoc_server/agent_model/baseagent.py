from abc import ABCMeta, abstractmethod
from mesa import Agent
from simoc_server.database.db_model import AgentType, AgentEntity, AgentAttribute
from simoc_server import db
from uuid import uuid4

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
            for agent_type_attribute in agent_type.agent_type_attributes:
                value_str = agent_type_attribute.value
                value_type = eval(agent_type_attribute.value_type)
                attr_name = agent_type_attribute.name
                self.__class__.agent_type_attributes[attr_name] = value_type(value_str)
            __agent_type_attributes_loaded__ = True
            self.__class__.__agent_type__ = agent_type

    def get_agent_type_attribute(self, name):
        return self.__class__.agent_type_attributes[name]

    def load_from_db(self):
        self.pos = (self.agent_entity.pos_x, self.agent_entity.pos_y)
        self.unique_id = self.agent_entity.agent_unique_id
        for attribute in self.agent_entity.agent_attributes:
            # get type of attribute
            value_type = eval(attribute.value_type)
            value_str = attribute.value
            self.__dict__[attribute] = value_type(value_str)

    def create_entity(self, model, unique_id):
        agent_entity = AgentEntity(agent_type=self.__class__.__agent_type__,
                 agent_model_entity=model.agent_model_entity, agent_unique_id=unique_id)
        for attribute_name in self.persisted_attributes:
            value = self.__dict__[attribute_name]
            value_type = type(value).__name__
            value_str = str(value)
            if value_type == type(None).__name__:
                raise Exception("None type not allowed for persistent attribute")
            agent_entity.agent_attributes.append(AgentAttribute(name=attribute_name, 
                value=value_str, value_type=value_type))
        return agent_entity

    def register_persisted_attribute(self, attribute_name):
        self.persisted_attributes.add(attribute_name)

    def register_client_attribute(self, attribute_name):
        self.client_attributes.add(attribute_name)

    def get_sprite_mapping(self):
        return self.sprite_mapper.get_sprite_mapping(self)

    def save(self, commit=True):
        for agent_attribute in self.agent_entity.agent_attributes:
            agent_attribute.value = self.__dict__[agent_attribute.name]
            db.session.add(agent_attribute)
        db.session.add(self.agent_entity)
        if commit:
            db.session.commit()