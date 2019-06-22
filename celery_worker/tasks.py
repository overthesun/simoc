import sys

from celery import Celery
from celery import current_task

sys.path.append("../")

from simoc_server.database.db_model import User
from simoc_server.game_runner import GameRunnerManager, GameRunnerInitializationParams
from simoc_server.exceptions import NotFound

app = Celery('tasks')
app.config_from_object('celery_worker.celeryconfig')

game_runner_manager = GameRunnerManager()


def get_user(username):
    user = User.query.filter_by(username=username).all()
    if len(user) != 1:
        raise NotFound(f'User {username} not found.')
    else:
        return user[0]


@app.task
def load_game(username, saved_game):
    game_runner_manager.load_game(get_user(username), saved_game)


@app.task
def save_game(username, save_name):
    game_runner_manager.save_game(get_user(username), save_name)


@app.task
def new_game(username, game_config):
    user = get_user(username)
    game_runner_init_params = GameRunnerInitializationParams(game_config)
    game_runner_manager.new_game(user, game_runner_init_params)
    game_runner = game_runner_manager.get_game_runner(user)
    return dict(worker_hostname=current_task.request.hostname, game_id=game_runner.game_id)


@app.task
def get_step_to(username, num_steps):
    game_runner_manager.get_step_to(get_user(username), num_steps)
