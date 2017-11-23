from flask_sqlalchemy import SQLAlchemy
from simoc_server import app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)


class User(UserMixin):
	
	def __init__(self, id, name, password):
		super(User, self).__init__()
		self.id = id
		self.name = name
		self.set_password(password)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def validate_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_id(self):
		return str(id)