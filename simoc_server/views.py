import datetime
from simoc_server import app, db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, session, jsonify
from simoc_server.database.db_model import User
from uuid import uuid4
from .game_runner import GameRunner
from . import error_handlers


login_manager = LoginManager()
login_manager.init_app(app)

game_runners = {}

@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    user = User.query.filter_by(username=username).first()
    if user and user.validate_password(password):
        login_user(user)
        return success("Logged In.")
    raise error_handlers.InvalidLogin("Bad username or password.")

@app.route("/register", methods=["POST"])
def register():
    username = request.json["username"]
    password = request.json["password"]
    if(User.query.filter_by(username=username).first()):
        raise error_handlers.BadRegistration("User already exists")
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return success("Registration complete.")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return success("Logged Out.")

@app.route("/auth_required", methods=["GET"])
@login_required
def authenticated_view():
    return success("Good to go.")

@app.route("/new_game", methods=["POST"])
@login_required
def new_game():
    game_runner = GameRunner.from_new_game(current_user)
    game_runner_id = uuid4()
    game_runners[game_runner_id] = game_runner
    session["game_runner_id"] = game_runner_id
    return success("New game created.")

@app.route("/get_step", methods=["GET"])
@login_required
def get_step():
    step_num = request.args.get("step_num", type=int)
    game_runner = get_game_runner()
    agent_model_state = game_runner.get_step(step_num)
    return jsonify(agent_model_state)

@app.route("/save_game", methods=["POST"])
@login_required
def save_game():
    if "save_name" in request.json.keys():
        save_name = request.json["save_name"]
    else:
        save_name = None
    game_runner = get_game_runner()
    game_runner.save_game(save_name)
    return success("Save successful.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_game_runner():
    if "game_runner_id" not in session.keys():
        raise error_handlers.BadRequest("No game found in session.")
    game_runner_id = session["game_runner_id"]
    if game_runner_id not in game_runners.keys():
        raise error_handlers.BadRequest("Game not found.")
    game_runner = game_runners[game_runner_id]
    return game_runner

def success(message, status_code=200):
    response = jsonify(
        {
            "message":message
        })
    response.status_code = status_code
    return response