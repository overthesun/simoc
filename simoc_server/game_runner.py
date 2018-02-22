import threading
import datetime
import time
import traceback

from simoc_server.exit_handler import register_exit_handler
from simoc_server.exceptions import GameNotFoundException, Unauthorized
from simoc_server import db, app
from simoc_server.agent_model import (AgentModel,
    AgentModelInitializationParams, DefaultAgentInitializerRecipe)
from simoc_server.serialize import AgentModelDTO
from simoc_server.database import SavedGame
from simoc_server.database.db_model import User

class GameRunner(object):

    def __init__(self, agent_model, user, step_buffer_size=10):
        self.agent_model = agent_model
        self.user = user
        self.step_buffer_size = step_buffer_size
        self.step_thread = None
        self.step_buffer = {}
        self.reset_last_accessed()

    @property
    def seconds_since_last_accessed(self):
        return time.time() - self.last_accessed

    @property
    def last_step_is_saved(self):
        return self.last_saved_step == self.agent_model.step_num

    @classmethod
    def load_from_state(cls, agent_model_state, user, step_buffer_size=10):
        if agent_model_state is None:
            raise Exception("Got None for agent_model_state.")
        agent_model = AgentModel.load_from_db(agent_model_state)
        agent_model.last_saved_step = agent_model.step_num
        return GameRunner(agent_model, user, step_buffer_size=step_buffer_size)

    @classmethod
    def load_from_saved_game(cls, user, saved_game, step_buffer_size=10):
        agent_model_state = saved_game.agent_model_snapshot.agent_model_state
        saved_game_user = saved_game.user
        if saved_game_user != user:
            raise Unauthorized("Attempted to load game belonging to another"
                "user.")
        return GameRunner.load_from_state(agent_model_state, user, step_buffer_size)

    @classmethod
    def from_new_game(cls, user, game_runner_init_params, step_buffer_size=10):
        agent_model = AgentModel.create_new(game_runner_init_params.model_init_params,
                                            game_runner_init_params.agent_init_recipe)
        agent_model.last_saved_step = None
        return GameRunner(agent_model, user, step_buffer_size=step_buffer_size)

    def save_game(self, save_name):
        with app.app_context():
            self.user = db.session.merge(self.user)
            agent_model_snapshot = self.agent_model.snapshot(commit=False)
            saved_game = SavedGame(user=self.user, agent_model_snapshot=agent_model_snapshot, name=save_name)
            db.session.add(saved_game)
            db.session.commit()
        self.last_saved_step = self.agent_model.step_num
        return saved_game

    def get_step(self, step_num=None):
        if(step_num is None):
            step_num = self.agent_model.step_num + 1
        self._step_to(step_num, False)
        return self._get_step_from_buffer(step_num)

    def reset_last_accessed(self):
        self.last_accessed = time.time()

    def _get_step_from_buffer(self, step_num):
        pruned_buffer = {}
        for n, step in self.step_buffer.items():
            if n > step_num:
                pruned_buffer[n] = step

        if step_num not in self.step_buffer.keys():
            all_step_nums = self.step_buffer.keys()
            min_step = min(all_step_nums) if len(all_step_nums) > 0 else None
            max_step = max(all_step_nums) if len(all_step_nums) > 0 else None
            raise Exception("Error step requested is out of range"
                "of buffer - min: {0} max: {1}".format(min_step, max_step))
        step = self.step_buffer[step_num]
        self.step_buffer = pruned_buffer

        if len(self.step_buffer) < self.step_buffer_size:
            self._step_to(step_num + self.step_buffer_size, True)

        return step

    def _step_to(self, step_num, threaded):
        # join to previous thread to prevent
        # more than 1 thread attempting to calculate steps
        if self.step_thread is not None and self.step_thread.isAlive():
            self.step_thread.join()
        def step_loop(agent_model,step_num, step_buffer):
            while self.agent_model.step_num < step_num:
                agent_model.step()
                step_buffer[self.agent_model.step_num] = AgentModelDTO(self.agent_model).get_state()
        if threaded:
            self.step_thread = threading.Thread(target=step_loop, \
                args=(self.agent_model,step_num, self.step_buffer))
            self.step_thread.run()
        else:
            step_loop(self.agent_model, step_num, self.step_buffer)

class GameRunnerInitializationParams(object):

    def __init__(self):
        # placeholder
        # TODO create agent model intialization parameters
        # from higher level game runner initialization parameters
        self.model_init_params = AgentModelInitializationParams()
        (self.model_init_params.set_grid_width(100)
                    .set_grid_height(100)
                    .set_starting_model_time(datetime.timedelta()))
        self.agent_init_recipe = DefaultAgentInitializerRecipe()


class GameRunnerManager(object):

    # time until GameRunner timesout and gets cleaned up
    TIMEOUT_INTERVAL = 120 # seconds
    CLEANUP_MAX_INTERVAL = 10 # seconds

    def __init__(self):
        self.game_runners = {}

        def cleanup_at_interval():
            self.clean_up_inactive()
            new_interval = self.get_next_timeout()
            self.cleanup_thread = threading.Timer(new_interval, cleanup_at_interval)
            self.cleanup_thread.start()

        def close():
            print("Closing cleanup thread..")
            self.cleanup_thread.cancel()
            print("Cleanup thread closed.")
            self.save_all(allow_repeat_save=False) # do not save if already saved

        register_exit_handler(close)
        self.cleanup_thread = threading.Timer(self.CLEANUP_MAX_INTERVAL, cleanup_at_interval)
        self.cleanup_thread.start()


    def new_game(self, user, game_runner_init_params):
        game_runner = GameRunner.from_new_game(user, game_runner_init_params)
        self._add_game_runner(user, game_runner)

    def load_game(self, user, saved_game):
        game_runner = GameRunner.load_from_saved_game(user, saved_game)
        self._add_game_runner(saved_game.user, game_runner)

    def save_all(self, allow_repeat_save=True):
        for user in self.game_runners.keys():
            self.save_game(user, allow_repeat_save=allow_repeat_save)

    def save_game(self, user, save_name=None, allow_repeat_save=True):
        game_runner = self.get_game_runner(user)

        if allow_repeat_save or not game_runner.last_step_is_saved:
            # only save if last step is not saved or
            # repeat save is allowed
            if game_runner is None:
                raise GameNotFoundException()

            if save_name is None:
                save_name = self._autosave_name()
            game_runner.save_game(save_name)

    def get_game_runner(self, user):
        try:
            if isinstance(user, User):
                return self.game_runners[user.id]
            else:
                user_id = user
                return self.game_runners[user_id]
        except KeyError:
            return None

    def get_step(self, user, step_num):
        game_runner = self.get_game_runner(user)
        if game_runner is None:
            raise GameNotFoundException()

        return game_runner.get_step(step_num)

    def _add_game_runner(self, user, game_runner):
        old_game = self.get_game_runner(user)
        if old_game is not None:
            old_game.save_game(self._autosave_name())

        self.game_runners[user.id] = game_runner

    def _autosave_name(self):
        return "{} {}".format(
                    "Autosave",
                    datetime.datetime.utcnow())

    def clean_up_inactive(self):
        marked_for_cleanup = []
        for user_id, game_runner in self.game_runners.items():
            if(game_runner.seconds_since_last_accessed > self.TIMEOUT_INTERVAL):
                marked_for_cleanup.append(user_id)

        for user_id in marked_for_cleanup:
            try:
                # prevent exceptions that would kill thread at all costs
                app.logger.info("Cleaning up save game for user with id {}".format(user_id))
                self.save_game(user_id)
                del self.game_runners[user_id]
            except KeyError as e:
                app.logger.error("Session for user '{}' removed before it could be cleaned up."
                                .format(user_id))
            except Exception as e:
                app.logger.error("Unknown exception occured in game manager cleanup.")
                traceback.print_exc()

    def get_next_timeout(self):
        next_timeouts = [self.TIMEOUT_INTERVAL - runner.seconds_since_last_accessed 
            for runner in self.game_runners.values()]
        return max(0, min([self.TIMEOUT_INTERVAL] + next_timeouts))
