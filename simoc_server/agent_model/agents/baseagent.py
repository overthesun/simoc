from abc import ABCMeta, abstractmethod
from mesa import Agent
from uuid import uuid4

from simoc_server import db
from simoc_server.util import load_db_attributes_into_dict, extend_dict
from simoc_server.database.db_model import AgentType, AgentState, AgentStateAttribute
from simoc_server.agent_model.sprite_mappers import DefaultSpriteMapper
from simoc_server.agent_model.agent_attribute_meta import AgentAttributeHolder

PERSISTABLE_ATTRIBUTE_TYPES = [int.__name__, float.__name__, str.__name__, type(None).__name__]

class BaseAgent(Agent, AgentAttributeHolder):
    __metaclass__ = ABCMeta

    _sprite_mapper = DefaultSpriteMapper
    _agent_type_name = None

    # Used to ensure type attributes are properly inherited and 
    # only loaded once
    _last_loaded_type_attr_class = False


    def __init__(self, model, agent_state=None):
        self.__class__._load_agent_type_attributes()
        AgentAttributeHolder.__init__(self)

        self.active = True
        if agent_state is not None:
            self.load_from_db(agent_state)
            super().__init__(self.unique_id, model)
        else:
            self.unique_id = "{0}_{1}".format(self.__class__.__name__, uuid4())
            self.model_time_created = model.model_time
            super().__init__(self.unique_id, model)

    @classmethod
    def _load_agent_type_attributes(cls):
        """ Load the agent type attributes from database into class.
            These agent type attributes should be static values that
            define the behaviors of a particular *class* of agents.
            They do not define instance level behavoirs or traits.

        Raises
        ------
        Exception
            If class does not define _agent_type_name or if the specified
            agent type cannot be located in the database
        """
        if not cls._agent_type_name:
            raise Exception("_agent_type_name not set")
        if cls._last_loaded_type_attr_class is not cls:
            agent_type_name = cls._agent_type_name
            agent_type = AgentType.query.filter_by(name=agent_type_name).first()
            if agent_type is None:
                raise Exception("Cannot find agent_type in database with name '{0}'".format(agent_type_name))

            attributes = {}

            # load bases in reversed order to preserve python-like inheritance
            # ie: first parent class defined takes precedence over second parent class
            # example: Child(ParentA, ParentB) -> the child class would get attributes
            # defined by ParentA, then ParentB and ParentB could not override ParentA attributes
            for base in reversed(cls.__bases__):
                if base is not BaseAgent and issubclass(base, BaseAgent):
                    base._load_agent_type_attributes()

                    # load this base class' attributes into existing set of attributes,
                    # overriding if necessary
                    attributes.update(base.agent_type_attributes)

            # finally, extend existing attributes with this classes attributes
            load_db_attributes_into_dict(agent_type.agent_type_attributes, attributes)
            cls.agent_type_attributes = attributes
            cls._last_loaded_type_attr_class = cls

            # store agent type id for later saving of agent state
            cls.__agent_type_id__ = agent_type.id

    def get_agent_type(self):
        """
        Returns
        -------
        AgentType
            Returns the AgentType related to the instance Agent
        """
        return AgentType.query.get(self.__class.__agent_type_id__)

    def get_agent_type_attribute(self, name):
        """ Get agent type attribute by name as it was defined in database

        Parameters
        ----------
        name : str
            The name of the attribute to return

        Returns
        -------
        Type of the Agent Attribute
            The value of the agent attribute with the given name
        """
        return self.__class__.agent_type_attributes[name]

    def load_from_db(self, agent_state):
        """ Load agent with the given state

        Parameters
        ----------
        agent_state : AgentState
            AgentState loaded from database to initialize the agent from
        """
        if agent_state.pos_x is not None and agent_state.pos_y is not None:
            self.pos = (agent_state.pos_x, agent_state.pos_y)
        self.unique_id = agent_state.agent_unique_id
        self.model_time_created = agent_state.model_time_created

        self.requires_post_load = {}

        load_db_attributes_into_dict(agent_state.agent_state_attributes, self.__dict__)

    def post_db_load(self):
        for name, attribute_descriptor in self.attribute_descriptors.items():
            if(issubclass(attribute_descriptor._type, BaseAgent)):
                id_value = self.__dict__[name]
                if id_value is not None:
                    self.__dict__[name] = self.model.agent_by_id(id_value)

    def snapshot(self, agent_model_state, commit=True):
        pos = self.pos if hasattr(self, "pos") else (None, None)
        agent_state = AgentState(agent_type_id=self.__class__.__agent_type_id__,
                 agent_model_state=agent_model_state, agent_unique_id=self.unique_id,
                 model_time_created=self.model_time_created, pos_x=pos[0], pos_y=pos[1])

        for attribute_name, attribute_descriptor in self.attribute_descriptors.items():
            value = self.__dict__[attribute_name]
            value_type = attribute_descriptor._type
            if issubclass(value_type, BaseAgent):
                value_type_str = "str"
                if value is not None:
                    value = value.unique_id
            else:
                value_type_str =  value_type.__name__
            value_str = str(value)
            if value_type_str not in PERSISTABLE_ATTRIBUTE_TYPES:
                raise Exception("Attribute set to non-persistable type.")

            agent_state.agent_state_attributes.append(AgentStateAttribute(name=attribute_name, 
                value=value_str, value_type=value_type_str))
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