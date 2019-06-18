import sys

from celery import Celery
from celery import current_task

sys.path.append("../")

from simoc_server.database.db_model import User
from simoc_server.game_runner import GameRunnerManager, GameRunnerInitializationParams

app = Celery('tasks')
app.config_from_object('celery_worker.celeryconfig')

game_runner_manager = GameRunnerManager()


@app.task
def new_game(username, game_config):
    user = User.query.filter_by(username=username).first()
    game_runner_init_params = GameRunnerInitializationParams(game_config)
    game_runner_manager.new_game(user, game_runner_init_params)
    game_runner = game_runner_manager.get_game_runner(user)
    return dict(worker_hostname=current_task.request.hostname, game_id=game_runner.game_id)


@app.task
def get_step_to(username, num_steps):
    user = User.query.filter_by(username=username).first()
    game_runner_manager.get_step_to(user, num_steps)
