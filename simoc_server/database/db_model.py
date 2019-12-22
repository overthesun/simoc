import datetime

from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Index
from sqlalchemy.types import BigInteger
from sqlalchemy.dialects import sqlite
from werkzeug.security import generate_password_hash, check_password_hash

from simoc_server import db


class BaseEntity(db.Model):
    __abstract__ = True  # Prevent sql alchemy from creating a table for BaseEntity

    @declared_attr
    def date_created(cls):
        # work around to move columns to end of table
        return db.Column(db.DateTime, server_default=db.func.now())

    @declared_attr
    def date_modified(cls):
        # work around to move columns to end of table
        return db.Column(db.DateTime, server_default=db.func.now(),
                         server_onupdate=db.func.now())

    def _attr(self, name, default_value=None):
        if name not in self.__dict__.keys():
            self.__dict__[name] = default_value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)


class User(BaseEntity, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


class BaseAttribute(BaseEntity):
    # Base attribute, used to store generic information in string
    # format along with type data for conversion
    __abstract__ = True

    @declared_attr
    def name(cls):
        return db.Column(db.String(128), nullable=False)

    @declared_attr
    def value(cls):
        return db.Column(db.String(512))

    @declared_attr
    def value_type(cls):
        return db.Column(db.String(80))


class DescriptiveAttribute(BaseAttribute):
    # Extends base attribute by adding unit and description as columns
    __abstract__ = True

    @declared_attr
    def description(cls):
        return db.Column(db.String(512), nullable=True)


class AgentModelParam(DescriptiveAttribute):
    id = db.Column(db.Integer, primary_key=True)


class AgentType(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True, index=True)
    agent_class = db.Column(db.String(80), nullable=False, unique=False)


class AgentTypeAttribute(DescriptiveAttribute):
    id = db.Column(db.Integer, primary_key=True)
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), index=True,
                              nullable=False)
    agent_type = db.relationship("AgentType",
                                 backref=db.backref("agent_type_attributes", lazy=False,
                                                    cascade="all, delete-orphan"))


class AgentTypeAttributeDetails(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_type_attribute_id = db.Column(db.Integer, db.ForeignKey("agent_type_attribute.id"),
                                        nullable=False, index=True)
    agent_type_attribute = db.relationship("AgentTypeAttribute",
                                           backref=db.backref("attribute_details", lazy=False,
                                                              cascade="all, delete-orphan"))
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), nullable=False,
                              index=True)
    agent_type = db.relationship("AgentType")
    currency_type_id = db.Column(db.Integer, db.ForeignKey("currency_type.id"), nullable=True,
                                 index=True)
    currency_type = db.relationship("CurrencyType")
    units = db.Column(db.String(100), nullable=True)
    flow_unit = db.Column(db.String(100), nullable=True)
    flow_time = db.Column(db.String(100), nullable=True)
    weighted = db.Column(db.String(100), nullable=True)
    criteria_name = db.Column(db.String(100), nullable=True)
    criteria_limit = db.Column(db.String(100), nullable=True)
    criteria_value = db.Column(db.Float, nullable=True)
    criteria_buffer = db.Column(db.Float, nullable=True)
    deprive_unit = db.Column(db.String(100), nullable=True)
    deprive_value = db.Column(db.Float, nullable=True)
    is_required = db.Column(db.Integer, nullable=True)
    requires = db.Column(db.JSON, nullable=True)
    is_growing = db.Column(db.Integer, nullable=True)
    lifetime_growth_type = db.Column(db.String(100), nullable=True)
    lifetime_growth_center = db.Column(db.Float, nullable=True)
    lifetime_growth_min_value = db.Column(db.Float, nullable=True)
    lifetime_growth_max_value = db.Column(db.Float, nullable=True)
    lifetime_growth_min_threshold = db.Column(db.Float, nullable=True)
    lifetime_growth_max_threshold = db.Column(db.Float, nullable=True)
    lifetime_growth_invert = db.Column(db.Integer, nullable=True)
    lifetime_growth_noise = db.Column(db.Integer, nullable=True)
    lifetime_growth_scale = db.Column(db.Float, nullable=True)
    lifetime_growth_steepness = db.Column(db.Float, nullable=True)
    daily_growth_type = db.Column(db.String(100), nullable=True)
    daily_growth_center = db.Column(db.Float, nullable=True)
    daily_growth_min_value = db.Column(db.Float, nullable=True)
    daily_growth_max_value = db.Column(db.Float, nullable=True)
    daily_growth_min_threshold = db.Column(db.Float, nullable=True)
    daily_growth_max_threshold = db.Column(db.Float, nullable=True)
    daily_growth_invert = db.Column(db.Integer, nullable=True)
    daily_growth_noise = db.Column(db.Integer, nullable=True)
    daily_growth_scale = db.Column(db.Float, nullable=True)
    daily_growth_steepness = db.Column(db.Float, nullable=True)

    def get_data(self):
        return {'agent_type_attribute_id':  self.agent_type_attribute_id,
                'agent_type_id': self.agent_type_id,
                'currency_type_id': self.currency_type_id,
                'units': self.units,
                'flow_unit': self.flow_unit,
                'flow_time': self.flow_time,
                'weighted': self.weighted,
                'criteria_name': self.criteria_name,
                'criteria_limit': self.criteria_limit,
                'criteria_value': self.criteria_value,
                'criteria_buffer': self.criteria_buffer,
                'deprive_unit': self.deprive_unit,
                'deprive_value': self.deprive_value,
                'is_required': self.is_required,
                'requires': self.requires,
                'is_growing': self.is_growing,
                'lifetime_growth_type': self.lifetime_growth_type,
                'lifetime_growth_center': self.lifetime_growth_center,
                'lifetime_growth_min_value': self.lifetime_growth_min_value,
                'lifetime_growth_max_value': self.lifetime_growth_max_value,
                'daily_growth_type': self.daily_growth_type,
                'daily_growth_center': self.daily_growth_center,
                'daily_growth_min_value': self.daily_growth_min_value,
                'daily_growth_max_value': self.daily_growth_max_value,
                'lifetime_growth_min_threshold': self.lifetime_growth_min_threshold,
                'lifetime_growth_max_threshold': self.lifetime_growth_max_threshold,
                'daily_growth_min_threshold': self.daily_growth_min_threshold,
                'daily_growth_max_threshold': self.daily_growth_max_threshold,
                'daily_growth_invert': self.daily_growth_invert,
                'lifetime_growth_invert': self.lifetime_growth_invert,
                'daily_growth_noise': self.daily_growth_noise,
                'lifetime_growth_noise': self.lifetime_growth_noise,
                'daily_growth_scale': self.daily_growth_scale,
                'lifetime_growth_scale': self.lifetime_growth_scale,
                'daily_growth_steepness': self.daily_growth_steepness,
                'lifetime_growth_steepness': self.lifetime_growth_steepness}


class CurrencyType(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)


class AgentState(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_model_state_id = db.Column(db.Integer, db.ForeignKey("agent_model_state.id"),
                                     nullable=False, index=True)
    agent_model_state = db.relationship("AgentModelState",
                                        backref=db.backref("agent_states", lazy=False,
                                                           cascade="all, delete-orphan"))
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), nullable=False)
    agent_type = db.relationship("AgentType")
    agent_unique_id = db.Column(db.String(100), nullable=False)
    model_time_created = db.Column(db.Interval(), nullable=False)
    agent_id = db.Column(db.Integer, nullable=True)
    active = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Float, nullable=True)
    amount = db.Column(db.Integer, nullable=True)
    lifetime = db.Column(db.Integer, nullable=True)
    connections = db.Column(db.String(2048), nullable=True)
    buffer = db.Column(db.String(2048), nullable=True)
    deprive = db.Column(db.String(2048), nullable=True)
    attributes = db.Column(db.String(2048), nullable=False)


class AgentStateAttribute(BaseAttribute):
    id = db.Column(db.Integer, primary_key=True)
    agent_state_id = db.Column(db.Integer, db.ForeignKey("agent_state.id"), nullable=False,
                               index=True)
    agent_state = db.relationship("AgentState",
                                  backref=db.backref("agent_state_attributes", lazy=False,
                                                     cascade="all, delete-orphan"))


class StepRecord(BaseEntity):
    id = db.Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    user = db.relationship("User")
    step_num = db.Column(db.Integer, nullable=False, index=True)
    game_id = db.Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), nullable=False, index=True)
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), nullable=False,
                              index=True)
    agent_type = db.relationship("AgentType", foreign_keys=[agent_type_id])
    agent_id = db.Column(db.BigInteger, nullable=False)
    agent_amount = db.Column(db.Integer, nullable=False)
    direction = db.Column(db.String(10), nullable=False, index=True)
    currency_type_id = db.Column(db.Integer, db.ForeignKey("currency_type.id"), nullable=False,
                                 index=True)
    currency_type = db.relationship("CurrencyType")
    value = db.Column(db.Float, nullable=False)
    growth = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(10), nullable=False)
    storage_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), nullable=False,
                                index=True)
    storage_type = db.relationship("AgentType", foreign_keys=[storage_type_id])
    storage_id = db.Column(db.Integer, nullable=False)
    storage_agent_id = db.Column(db.BigInteger, nullable=False)
    __table_args__ = (Index('step_user_game_idx', "user_id", "game_id"),)

    def get_data(self):
        return {'user_id': self.user_id,
                'username': self.user.username,
                "step_num": self.step_num,
                'game_id': self.game_id,
                "agent_type": self.agent_type.name,
                "agent_id": self.agent_id,
                "agent_amount": self.agent_amount,
                "direction": self.direction,
                "currency_type": self.currency_type.name,
                "currency_type_id": self.currency_type.id,
                "value": self.value,
                "growth": self.max_value,
                "unit": self.unit,
                "storage_type": self.storage_type.name,
                "storage_id": self.storage_id,
                "storage_agent_id": self.storage_agent_id}


class ModelRecord(BaseEntity):
    id = db.Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    user = db.relationship("User")
    start_time = db.Column(db.Integer, nullable=False)
    game_id = db.Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), nullable=False, index=True)
    step_num = db.Column(db.Integer, nullable=False, index=True)
    hours_per_step = db.Column(db.Float, nullable=False)
    is_terminated = db.Column(db.String(10), nullable=False)
    time = db.Column(db.Float, nullable=False)
    termination_reason = db.Column(db.String(100), nullable=True)
    __table_args__ = (Index('model_user_game_idx', "user_id", "game_id"),)

    def get_data(self):
        return {'user_id': self.user_id,
                'username': self.user.username,
                'start_time': self.start_time,
                'game_id': self.game_id,
                "step_num": self.step_num,
                "hours_per_step": self.hours_per_step,
                "is_terminated": self.is_terminated,
                "time": self.time,
                "termination_reason": self.termination_reason}

    def get_all_data(self):
        return {'user_id': self.user_id,
                'username': self.user.username,
                'start_time': self.start_time,
                'game_id': self.game_id,
                "step_num": self.step_num,
                "hours_per_step": self.hours_per_step,
                "is_terminated": self.is_terminated,
                "time": self.time,
                "termination_reason": self.termination_reason,
                "agent_type_counts": [i.get_data() for i in self.agent_type_counters],
                "storage_capacities": [i.get_data() for i in self.storage_capacities]}


class AgentTypeCountRecord(BaseEntity):
    id = db.Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True)
    model_record_id = db.Column(db.BigInteger, db.ForeignKey("model_record.id"), nullable=False,
                                index=True)
    model_record = db.relationship("ModelRecord",
                                   backref=db.backref("agent_type_counters", lazy=False,
                                                    cascade="all, delete-orphan"))
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), nullable=False,
                              index=True)
    agent_type = db.relationship("AgentType")
    agent_counter = db.Column(db.Integer, nullable=False)

    def get_data(self):
        return {"agent_type": self.agent_type.name,
                "agent_counter": self.agent_counter}


class StorageCapacityRecord(BaseEntity):
    id = db.Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True)
    model_record_id = db.Column(db.BigInteger, db.ForeignKey("model_record.id"), nullable=False,
                                index=True)
    model_record = db.relationship("ModelRecord",
                                   backref=db.backref("storage_capacities", lazy=False,
                                                      cascade="all, delete-orphan"))
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), nullable=False,
                              index=True)
    agent_type = db.relationship("AgentType")
    agent_id = db.Column(db.BigInteger, nullable=False)
    storage_id = db.Column(db.BigInteger, nullable=False, index=True)
    currency_type_id = db.Column(db.Integer, db.ForeignKey("currency_type.id"), nullable=True,
                                 index=True)
    currency_type = db.relationship("CurrencyType")
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Float, nullable=False)

    def get_data(self):
        return {"agent_type": self.agent_type.name,
                "agent_id": self.agent_id,
                "currency_type": self.currency_type.name,
                "currency_type_id": self.currency_type.id,
                "value": self.value,
                "unit": self.unit,
                "capacity": self.capacity}


class AgentModelState(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    step_num = db.Column(db.Integer, nullable=False)
    grid_width = db.Column(db.Integer, nullable=False)
    grid_height = db.Column(db.Integer, nullable=False)
    model_time = db.Column(db.Interval, nullable=False)
    seed = db.Column(db.BigInteger, nullable=False)
    random_state = db.Column(db.PickleType, nullable=False)
    termination = db.Column(db.String(2048), nullable=False)
    priorities = db.Column(db.String(2048), nullable=False)
    location = db.Column(db.String(2048), nullable=False)
    minutes_per_step = db.Column(db.Integer, nullable=False)
    config = db.Column(db.Text(10240), nullable=False)


class AgentModelSnapshot(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_model_state_id = db.Column(db.Integer, db.ForeignKey("agent_model_state.id"))
    agent_model_state = db.relationship("AgentModelState",
                                        backref=db.backref("agent_model_snapshot", uselist=False))
    snapshot_branch_id = db.Column(db.Integer, db.ForeignKey("snapshot_branch.id"))
    snapshot_branch = db.relationship("SnapshotBranch",
                                      backref=db.backref("agent_model_snapshots", lazy=True))


class SnapshotBranch(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, nullable=False)
    __mapper_args__ = {
        "version_id_col": version_id
    }
    parent_branch_id = db.Column(db.Integer, db.ForeignKey("snapshot_branch.id"))
    parent_branch = db.relationship("SnapshotBranch", backref=db.backref("child_branches"),
                                    remote_side=[id])

    def get_root_branch(self):
        node = self
        while node.parent_branch is not None:
            node = node.parent_branch
        return node


class SavedGame(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), default=lambda: str(datetime.datetime.utcnow()))
    agent_model_snapshot_id = db.Column(db.Integer, db.ForeignKey("agent_model_snapshot.id"))
    agent_model_snapshot = db.relationship("AgentModelSnapshot")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")
