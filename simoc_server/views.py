from simoc_server import app
from flask_login import LoginManager, login_user
from flask import request
from simoc_server.database.db_model import User

app.secret_key = '$$#@AS]d##$ADVH]]3$^s&*!acgs'

login_manager = LoginManager()
login_manager.init_app(app)

test_users = {
	"0":User(0, "bob", "bad_pass"),
	"1":User(1, "steve", "pass123")
}

def get_user(username):
	for user in test_users.values():
		print(user)
		if user.name == username:
			return user
	return None

@app.route("/login", methods=["POST"])
def login():
	username = request.json["username"]
	password = request.json["password"]
	user = get_user(username)
	if user and user.validate_password(password):
		login_user(user)
		return "logged in"
	return "invalid login"


@login_manager.user_loader
def load_user(user_id):
	if user_id in test_users.keys():
		return test_users[user_id]
	else:
		return None