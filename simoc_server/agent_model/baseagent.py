from abc import ABCMeta, abstractmethod
from mesa import Agent
from uuid import uuid4

from simoc_server import db
from simoc_server.util.db_util import load_db_attributes_into_dict
from simoc_server.database.db_model import AgentType, AgentState, AgentStateAttribute
from simoc_server.agent_model.sprite_mappers import DefaultSpriteMapper
from simoc_server.agent_model.agent_attribute_meta import AgentAttributeHolder

PERSISTABLE_ATTRIBUTE_TYPES = [int.__name__, float.__name__, str.__name__, type(None).__name__]

class BaseAgent(Agent, AgentAttributeHolder):
    __metaclass__ = ABCMeta

    __sprite_mapper__ = DefaultSpriteMapper
    __agent_type_name__ = None
    __agent_type_attributes_loaded__ = False


    def __init__(self, model, agent_state=None):
        self.load_agent_type_attributes()

        self.active = True
        if agent_state is not None:
            self.load_from_db(agent_state)
            super().__init__(self.unique_id, model)
        else:
            self.unique_id = "{0}_{1}".format(self.__class__.__name__, uuid4())
            self.model_time_created = model.model_time
            super().__init__(self.unique_id, model)

    def load_agent_type_attributes(self):
        if not self.__class__.__agent_type_name__:
            raise Exception("__agent_type_name__ not set")
        if not self.__class__.__agent_type_attributes_loaded__:
            agent_type_name = self.__class__.__agent_type_name__
            agent_type = AgentType.query.filter_by(name=agent_type_name).first()
            if agent_type is None:
                raise Exception("Cannot find agent_type in database with name '{0}'".format(agent_type_name))

            try:
                load_db_attributes_into_dict(agent_type.agent_type_attributes, self.__class__.agent_type_attributes)
            except AttributeError:
                # agent_type_attributes not yet created in base c
            __agent_type_attributes_loaded__ = True
            self.__class__.__agent_type_id__ = agent_type.id

    def get_agent_type(self):
        return AgentType.query.get(self.__class.__agent_type_id__)

    def get_agent_type_attribute(self, name):
        return self.__class__.agent_type_attributes[name]

    def load_from_db(self, agent_state):
        self.pos = (agent_state.pos_x, agent_state.pos_y)
        self.unique_id = agent_state.agent_unique_id
        self.model_time_created = agent_state.model_time_created
        load_db_attributes_into_dict(agent_state.agent_state_attributes, self.__dict__)

    def snapshot(self, agent_model_state, commit=True):
        agent_state = AgentState(agent_type_id=self.__class__.__agent_type_id__,
                 agent_model_state=agent_model_state, agent_unique_id=self.unique_id,
                 model_time_created=self.model_time_created, pos_x=self.pos[0], pos_y=self.pos[1])

        for attribute_name, attribute_descriptor in self.attribute_descriptors.items():
            value = self.__dict__[attribute_name]
            value_type = attribute_descriptor._type.__name__
            value_str = str(value)
            if value_type not in PERSISTABLE_ATTRIBUTE_TYPES:
                raise Exception("Attribute set to non-persistable type.")

            agent_state.agent_state_attributes.append(AgentStateAttribute(name=attribute_name, 
                value=value_str, value_type=value_type))
        db.session.add(agent_state)
        if commit:
            db.session.commit()

    def get_sprite_mapping(self):
        return self.sprite_mapper.get_sprite_mapping(self)

    def status_str(self):
        sb = []
        for attribute_name, attribute_descriptor in self.attribute_descriptors.items():
            sb.append("{0}: {1}".format(attribute_name, self.__dict__[attribute_name]))
        return " ".join(sb)

    def destroy(self):
        self.active = False
        self.model.remove(self)