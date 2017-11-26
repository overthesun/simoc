from abc import ABCMeta, abstractmethod
from mesa import Agent
from simoc_server.database.db_model import AgentType, AgentState, AgentStateAttribute
from simoc_server import db
from uuid import uuid4

PERSISTABLE_ATTRIBUTE_TYPES = [int.__name__, float.__name__, str.__name__, type(None).__name__]

class BaseAgent(Agent):
    __metaclass__ = ABCMeta

    __agent_type_name__ = None
    __agent_type_attributes_loaded__ = False

    def __init__(self, model, agent_state=None):
        self.type = self.__class__.__name__
        self.load_agent_type_attributes()
        #self.sprite_mapper = DefaultSpriteMapper
        self.persisted_attributes = set()
        self.client_attributes = set()
        if agent_state is not None:
            self.load_from_db(agent_state)
        else:
            self.unique_id = "{0}_{1}".format(self.__class__.__name__, uuid4())
            self.init_new()

        super().__init__(self.unique_id, model)

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

    def load_from_db(self, agent_state):
        self.pos = (agent_state.pos_x, agent_state.pos_y)
        self.unique_id = agent_state.agent_unique_id
        self.__class__._load_database_attributes_into(agent_state.agent_state_attributes,
            self.__dict__)
        for attribute in agent_state.agent_state_attributes:
            self.persisted_attributes.add(attribute.name)

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

    def snapshot(self, agent_model_state, commit=True):
        agent_state = AgentState(agent_type=self.__class__.__agent_type__,
                 agent_model_state=agent_model_state, agent_unique_id=self.unique_id,
                 pos_x=self.pos[0], pos_y=self.pos[1])
        for attribute_name in self.persisted_attributes:
            value_str, value_type = self._get_instance_attribute_params(attribute_name)
            agent_state.agent_state_attributes.append(AgentStateAttribute(name=attribute_name, 
                value=value_str, value_type=value_type))
        db.session.add(agent_state)
        if commit:
            db.session.commit()

    def status_str(self):
        sb = []
        for attribute_name in self.persisted_attributes:
            sb.append("{0}: {1}".format(attribute_name, self.__dict__[attribute_name]))
        return " ".join(sb)