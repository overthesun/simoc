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
    def details(cls):
        return db.Column(db.String(128), nullable=True)

    @declared_attr
    def description(cls):
        return db.Column(db.String(512), nullable=True)

    @declared_attr
    def growth(cls):
        return db.Column(db.Integer, nullable=True)


class AgentModelParam(DescriptiveAttribute):
    id = db.Column(db.Integer, primary_key=True)


class AgentType(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    agent_class = db.Column(db.String(80), nullable=False, unique=False)


class AgentTypeAttribute(DescriptiveAttribute):
    id = db.Column(db.Integer, primary_key=True)
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), index=True,
                              nullable=False)
    agent_type = db.relationship("AgentType",
                                 backref=db.backref("agent_type_attributes", lazy=False,
                                                    cascade="all, delete-orphan"))


class AgentState(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_model_state_id = db.Column(db.Integer, db.ForeignKey("agent_model_state.id"),
                                     nullable=False, index=True)
    agent_model_state = db.relationship("AgentModelState",
                                        backref=db.backref("agent_states", lazy=False,
                                                           cascade="all, delete-orphan"))
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"),
                              nullable=False)
    agent_type = db.relationship("AgentType")
    agent_unique_id = db.Column(db.String(120), nullable=False)
    model_time_created = db.Column(db.Interval(), nullable=False)
    agent_id = db.Column(db.Integer, nullable=True)
    active = db.Column(db.String(120), nullable=True)
    age = db.Column(db.Float, nullable=True)
    amount = db.Column(db.Integer, nullable=True)
    lifetime = db.Column(db.Integer, nullable=True)
    connections = db.Column(db.String(1000), nullable=True)
    buffer = db.Column(db.String(1000), nullable=True)
    deprive = db.Column(db.String(1000), nullable=True)
    attributes = db.Column(db.String(1000), nullable=False)


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
    grid_width = db.Column(db.Integer, nullable=False)
    grid_height = db.Column(db.Integer, nullable=False)
    model_time = db.Column(db.Interval, nullable=False)
    seed = db.Column(db.BigInteger, nullable=False)
    random_state = db.Column(db.PickleType, nullable=False)
    termination = db.Column(db.String(300), nullable=False)
    priorities = db.Column(db.String(300), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    minutes_per_step = db.Column(db.Integer, nullable=False)
    config = db.Column(db.String(300), nullable=False)
    logging = db.Column(db.String(300), nullable=False)
    logs = db.Column(db.String(1000), nullable=False)


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
