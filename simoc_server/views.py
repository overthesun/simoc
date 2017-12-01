import datetime
from simoc_server import app, db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, session, jsonify
from simoc_server.database.db_model import User, SavedGame
from uuid import uuid4
from .game_runner import GameRunner
from . import error_handlers
from collections import OrderedDict


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
    add_game_runner(game_runner)
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

@app.route("/load_game", methods=["POST"])
@login_required
def load_game():
    if "saved_game_id" in request.json.keys():
        saved_game_id = request.json["saved_game_id"]
    else:
        raise error_handlers.BadRequest("saved_game_id required.")
    saved_game = SavedGame.query.get(saved_game_id)
    if saved_game is None:
        raise error_handlers.NotFound("Requested game not found.")
    game_runner = GameRunner.load_from_saved_game(saved_game)
    add_game_runner(game_runner)
    return success("Game loaded successfully.")

@app.route("/get_saved_games", methods=["GET"])
@login_required
def get_saved_games():
    saved_games = SavedGame.query.filter_by(user=current_user).all()

    sequences = {}
    for saved_game in saved_games:
        snapshot = saved_game.agent_model_snapshot
        snapshot_branch = snapshot.snapshot_branch
        root_branch = snapshot_branch.get_root_branch()
        if(root_branch in sequences.keys()):
            sequences[root_branch].append(save_game)
        else:
            sequences[root_branch] = [saved_game]

    sequences = OrderedDict(sorted(sequences.items(), key=lambda x: x[0].date_created))

    response = {}
    for root_branch, saved_games in sequences.items():
        response[root_branch.id] = []
        for saved_game in saved_games:
            response[root_branch.id].append({
                "saved_game_id":saved_game.id,
                "name":saved_game.name,
                "date_created":saved_game.date_created
            })
    return jsonify(response)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_game_runner():
    if "game_runner_id" not in session.keys():
        raise error_handlers.BadRequest("No game found in session.")
    game_runner_id = session["game_runner_id"]
    if game_runner_id not in game_runners.keys():
        raise error_handlers.NotFound("Game not found.")
    game_runner = game_runners[game_runner_id]
    return game_runner

def add_game_runner(game_runner):
    game_runner_id = uuid4()
    game_runners[game_runner_id] = game_runner
    session["game_runner_id"] = game_runner_id
    return game_runner_id

def success(message, status_code=200):
    print(message)
    response = jsonify(
        {
            "message":message
        })
    response.status_code = status_code
    return response