import sys
import time

from celery import Celery
from celery import current_task
from celery.utils.log import get_task_logger
from celery.signals import worker_process_init
from celery.concurrency import asynpool
asynpool.PROC_ALIVE_TIMEOUT = 100.0

logger = get_task_logger(__name__)

sys.path.append("../")

from simoc_server.database.db_model import User
from simoc_server.game_runner import GameRunnerManager, GameRunnerInitializationParams
from simoc_server.exceptions import NotFound
from simoc_server import redis_conn, db

app = Celery('tasks')
app.config_from_object('celery_worker.celeryconfig')

game_runner_manager = None


@worker_process_init.connect
def on_worker_init(**kwargs):
    del kwargs
    global game_runner_manager
    game_runner_manager = GameRunnerManager()
    logger.info('GameRunnerManager initialized.')


def get_user(username, num_retries=30, interval=1):
    while True:
        try:
            user = User.query.filter_by(username=username).all()
        except Exception:
            user = []
            db.session.rollback()
        if len(user) != 1:
            if num_retries > 0:
                num_retries -= 1
                db.session.rollback()
                time.sleep(interval)
            else:
                raise NotFound(f'User {username} not found.')
        else:
            return user[0]


# TODO: Disabled until save_game is fixed
# @app.task
# def load_game(username, saved_game_id, num_steps):
#     global game_runner_manager
#     saved_game = SavedGame.query.get(saved_game_id)
#     if saved_game is None:
#         raise NotFound(f'Saved game with Id {saved_game_id} not found.')
#     user = get_user(username)
#     game_runner_manager.load_game(user, saved_game)
#     game_runner = game_runner_manager.get_game_runner(user)
#     game_id = game_runner.game_id
#     redis_conn.set('task_mapping:{}'.format(game_id), load_game.request.id)
#     redis_conn.set('user_mapping:{}'.format(user.id), game_id)
#     redis_conn.set('worker_mapping:{}'.format(game_id), current_task.request.hostname)
#     game_runner_manager.get_step_to(user, num_steps)


# TODO: This route needs to be re-designed since `worker_direct` is no longer activated
# @app.task
# def save_game(username, save_name):
#     global game_runner_manager
#     game_runner_manager.save_game(get_user(username), save_name)


@app.task
def new_game(username, game_config, num_steps, expire=3600):
    global game_runner_manager
    user = get_user(username)
    game_runner_init_params = GameRunnerInitializationParams(game_config)
    try:
        game_runner_manager.new_game(user, game_runner_init_params)
    except:
        db.session.rollback()
        game_runner_manager.new_game(user, game_runner_init_params)
    game_runner = game_runner_manager.get_game_runner(user)
    game_id = game_runner.game_id
    redis_conn.set('task_mapping:{}'.format(game_id), new_game.request.id)
    redis_conn.set('worker_mapping:{}'.format(game_id), current_task.request.hostname)
    redis_conn.set('user_mapping:{}'.format(user.id), game_id)
    redis_conn.expire(f'task_mapping:{user.id}', expire)
    redis_conn.expire(f'worker_mapping:{game_id}', expire)
    redis_conn.expire(f'user_mapping:{user.id}', expire)
    try:
        game_runner_manager.get_step_to(user, num_steps)
    finally:
        redis_conn.delete('user_mapping:{}'.format(user.id))
