import datetime
from simoc_server import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class BaseEntity(db.Model):
    __abstract__ = True # Prevent sql alchemy from creating a table for BaseEntity

    date_created = db.Column(db.DateTime, server_default=db.func.now())
    date_modified = db.Column(db.DateTime, server_default=db.func.now(),
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

class AgentType(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)

class AgentTypeAttribute(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"), index=True,
        nullable=False)
    agent_type = db.relationship("AgentType",
        backref=db.backref("agent_type_attributes", lazy=False))
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80))
    value_type = db.Column(db.String(80))


class AgentState(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    pos_x = db.Column(db.Integer, nullable=True)
    pos_y = db.Column(db.Integer, nullable=True)
    agent_unique_id = db.Column(db.String(120), nullable=False)
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"),
        nullable=False)
    agent_type = db.relationship("AgentType")
    agent_model_state_id = db.Column(db.Integer, db.ForeignKey("agent_model_state.id"),
        nullable=False, index=True)
    agent_model_state = db.relationship("AgentModelState", backref=db.backref("agent_states", lazy=False))

class AgentStateAttribute(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_state_id = db.Column(db.Integer, db.ForeignKey("agent_state.id"), nullable=False, index=True)
    agent_state = db.relationship("AgentState", backref=db.backref("agent_state_attributes", lazy=False))
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80))
    value_type = db.Column(db.String(80))

class AgentModelState(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    step_num = db.Column(db.Integer, nullable=False)
    grid_width = db.Column(db.Integer, nullable=False)
    grid_height = db.Column(db.Integer, nullable=False)


class AgentModelSnapshot(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_model_state_id = db.Column(db.Integer, db.ForeignKey("agent_model_state.id"))
    agent_model_state = db.relationship("AgentModelState", backref=db.backref("agent_model_snapshot", uselist=False))
    previous_snapshot_id = db.Column(db.Integer, db.ForeignKey("agent_model_snapshot.id"))
    previous_snapshot = db.relationship("AgentModelSnapshot", backref=db.backref("next_snapshots", lazy=True),
        remote_side=[id])

class SavedGame(BaseEntity):
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(120), default=lambda:str(datetime.datetime.utcnow()))
     agent_model_snapshot_id = db.Column(db.Integer, db.ForeignKey("agent_model_snapshot.id"))
     agent_model_snapshot = db.relationship("AgentModelSnapshot")
     user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
     user = db.relationship("User")
