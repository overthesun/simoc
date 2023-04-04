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
from simoc_server.game_runner import GameRunnerManager
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
        except Exception as err:
            user = []
            logger.error(f'Exception in task.get_user({username=}) ({err}): rolling back')
            db.session.rollback()
        if len(user) != 1:
            logger.warning(f'User {username!r} NOT found ({num_retries=} left): {user=}')
            if num_retries > 0:
                num_retries -= 1
                db.session.rollback()
                time.sleep(interval)
            else:
                raise NotFound(f'User {username} not found.')
        else:
            logger.info(f'User found ({num_retries=} left): {user[0]}')
            return user[0]


@app.task
def new_game(username, game_config, num_steps, user_agent_desc=None,
             user_agent_conn=None, expire=3600):
    logger.info(f'Starting new game for {username=}, {num_steps=}')
    user = get_user(username)
    try:
        game_runner_manager.new_game(user, game_config, user_agent_desc,
                                     user_agent_conn)
    except Exception as err:
        db.session.rollback()
        logger.error(f'Exception in task.new_game ({err}): rolling back')
        game_runner_manager.new_game(user, game_config)
    game_runner = game_runner_manager.get_game_runner(user)
    game_id = game_runner.game_id
    logger.info(f'Setting user:{user.id} task:{game_id:X} on Redis')
    redis_conn.set('task_mapping:{}'.format(game_id), new_game.request.id)
    redis_conn.set('worker_mapping:{}'.format(game_id), current_task.request.hostname)
    redis_conn.set('user_mapping:{}'.format(user.id), game_id)
    redis_conn.expire(f'task_mapping:{user.id}', expire)
    redis_conn.expire(f'worker_mapping:{game_id}', expire)
    redis_conn.expire(f'user_mapping:{user.id}', expire)
    try:
        game_runner_manager.get_step_to(user, num_steps)
    finally:
        logger.info(f'Deleting user_mapping on Redis for {user}')
        redis_conn.delete('user_mapping:{}'.format(user.id))
