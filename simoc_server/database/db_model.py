import datetime

from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr
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

    def __repr__(self):
        return f'<User id={self.id} username={self.username}>'


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
    is_required = db.Column(db.String(100), nullable=True)
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


class AgentModelState(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    step_num = db.Column(db.Integer, nullable=False)
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
