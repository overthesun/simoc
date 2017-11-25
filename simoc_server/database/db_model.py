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
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"),
        nullable=False)
    agent_type = db.relationship("AgentType",
        backref=db.backref("agent_type_attributes", lazy=False))
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80))
    value_type = db.Column(db.String(80))


class AgentEntity(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_type_id = db.Column(db.Integer, db.ForeignKey("agent_type.id"),
        nullable=False)
    agent_type = db.relationship("AgentType")
    agent_model_entity_id = db.Column(db.Integer, db.ForeignKey("agent_model_entity.id"),
        nullable=False)
    agent_model_entity = db.relationship("AgentModelEntity", backref=db.backref("agent_entities", lazy=False))

class AgentAttribute(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
    agent_entity_id = db.Column(db.Integer, db.ForeignKey("agent_entity.id"), nullable=False)
    agent_entity = db.relationship("AgentEntity", backref=db.backref("agent_attributes", lazy=False))
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80))
    value_type = db.Column(db.String(80))

class AgentModelEntity(BaseEntity):
    id = db.Column(db.Integer, primary_key=True)
#     saved_game_id = db.Column(db.Integer, db.ForeignKey("saved_game.id"), nullable=False)
#     saved_game = db.relationship("SavedGame", backref=db.backref("saved_games", lazy=False))

# class SavedGame(BaseEntity):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     user = db.relationship("User")
