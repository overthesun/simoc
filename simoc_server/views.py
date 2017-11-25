from simoc_server import app
from flask_login import LoginManager, login_user, login_required, logout_user
from flask import request, session
from simoc_server.database.db_model import User

app.secret_key = '$$#@AS]d##$ADVH]]3$^s&*!acgs'

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    user = User.query.filter_by(username=username).first()
    if user and user.validate_password(password):
        login_user(user)
        return "logged in"
    return "invalid login"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "logged_out"

@app.route("/auth_required", methods=["GET"])
@login_required
def authenticated_view():
    return "good_to_go"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))