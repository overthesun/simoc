import datetime
import threading
import time
import traceback

from simoc_server import app, db
from simoc_server.agent_model import (AgentModel,
                                      AgentModelInitializationParams,
                                      BaseLineAgentInitializerRecipe)
from simoc_server.database import SavedGame
from simoc_server.database.db_model import (AgentTypeCountRecord,
                                            ModelRecord,
                                            StepRecord,
                                            StorageCapacityRecord,
                                            User)
from simoc_server.exceptions import GameNotFoundException, Unauthorized
from simoc_server.exit_handler import register_exit_handler, remove_exit_handler


class GameRunner(object):
    """Manages a game instance and the associated agent model.
    Runs the agent model and provides dictionary representations
    of the internal state of the model at steps.

    Attributes
    ----------
    agent_model : simoc_server.agent_model.AgentModel
        The agent model used by the game instance.
    last_accessed : float
        The time in seconds since Epoch when the game runner instance
        was last accessed
    last_saved_step : int
        The last step number that was saved.
    step_thread : Thread
        Internal worker thread used to precalculate steps and store in
        the step buffer.
    user : simoc_server.database.db_model.User
        The user the game belongs to
    """

    def __init__(self, agent_model, user, last_saved_step):
        self.agent_model = agent_model
        self.user = user
        self.step_thread = None
        self.last_saved_step = last_saved_step
        self.agent_model.user_id = self.user.id
        for log in ModelRecord.query.filter_by(user_id=user.id).all() + \
                   StepRecord.query.filter_by(user_id=user.id).all() + \
                   AgentTypeCountRecord.query.filter_by(user_id=user.id).all() + \
                   StorageCapacityRecord.query.filter_by(user_id=user.id).all():
            db.session.delete(log)
        db.session.commit()
        self.reset_last_accessed()

    @property
    def seconds_since_last_accessed(self):
        """
        Returns
        -------
        float
            Seconds since this game runner was last accessed.  'Accessed' is
            defined as requesting a step or pinging the server to explicitly keep the
            session alive, this can be used during a game pause for instance.  Used to
            check for timeout.
        """
        return time.time() - self.last_accessed

    @property
    def last_step_is_saved(self):
        """
        Returns
        -------
        bool
            Whether or not the last calculated step is saved.
        """
        return self.last_saved_step == self.agent_model.step_num

    @classmethod
    def load_from_state(cls, user, agent_model_state):
        """Loads a game runner for AgentModelState.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            User to associate the GameRunner with.
        agent_model_state : simoc_server.database.db_model.AgentModelState
            Agent model state to load the game runner from.

        Returns
        -------
        GameRunner
            loaded GameRunner instance
        """
        agent_model = AgentModel.load_from_db(agent_model_state)
        return GameRunner(agent_model, user, agent_model.step_num)

    @classmethod
    def load_from_saved_game(cls, user, saved_game):
        """Loads a game runner from a SavedGame

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            User to associate the GameRunner with.
        saved_game : simoc_server.database.db_model.SavedGame
            Saved game to load the game runner from.

        Returns
        -------
        GameRunner
            loaded GameRunner instance

        Raises
        ------
        Unauthorized
            If the user provided does not match the user the game was saved
            for.
        """
        agent_model_state = saved_game.agent_model_snapshot.agent_model_state
        saved_game_user = saved_game.user
        if saved_game_user != user:
            raise Unauthorized("Attempted to load game belonging to another"
                               "user.")
        return GameRunner.load_from_state(user, agent_model_state)

    @classmethod
    def from_new_game(cls, user, game_runner_init_params):
        """Creates a new game runner.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            User to associate the GameRunner with.
        game_runner_init_params : GameRunnerInitializationParams
            Initialization parameters to be used when loading the model.

        Returns
        -------
        GameRunner
            loaded GameRunner instance
        """
        agent_model = AgentModel.create_new(game_runner_init_params.model_init_params,
                                            game_runner_init_params.agent_init_recipe)
        return GameRunner(agent_model, user, None)

    def save_game(self, save_name):
        """Saves the game using the provided name and commits session to the
        database.

        Parameters
        ----------
        save_name : str
            The name to give the save.

        Returns
        -------
        simoc_server.database.db_model.SavedGame
            The saved game entity that was created.
        """
        self.user = db.session.merge(self.user)
        agent_model_snapshot = self.agent_model.snapshot(commit=False)
        saved_game = SavedGame(
            user=self.user, agent_model_snapshot=agent_model_snapshot, name=save_name)
        db.session.add(saved_game)
        db.session.commit()
        self.last_saved_step = self.agent_model.step_num
        return saved_game

    def ping(self):
        """Reset's the last accessed time.  Useful if the game is paused.
        """
        self.reset_last_accessed()

    def reset_last_accessed(self):
        """Reset the time since epoch that the game runner was last accessed at
        to the current time.
        """
        self.last_accessed = time.time()

    def step_to(self, step_num, threaded):
        """Run the agent model to the requested step.

        Parameters
        ----------
        step_num : int
            Step number to run the model to.
        threaded : bool
            Whether or not to run the model in a seperate thread.  If true
            and a thread already exists, first join then start a new thread.
        """

        # join to previous thread to prevent
        # more than 1 thread attempting to calculate steps
        if self.step_thread is not None and self.step_thread.isAlive():
            self.step_thread.join()

        def step_loop(agent_model, step_num, buffer_size=10):
            model_records = []
            while agent_model.step_num <= step_num and not agent_model.is_terminated:
                agent_model.step()
                model_records += agent_model.get_model_logs()
                if agent_model.step_num % buffer_size == 0:
                    db.session.add_all(StepRecord(**step) for step in agent_model.step_records)
                    db.session.add_all(model_records)
                    db.session.commit()
                    agent_model.step_records = []
                    model_records = []
            db.session.add_all(model_records)
            db.session.add_all(StepRecord(**step) for step in agent_model.step_records)
            db.session.commit()

        if threaded:
            self.step_thread = threading.Thread(target=step_loop,
                                                args=(self.agent_model, step_num))
            self.step_thread.run()
        else:
            step_loop(self.agent_model, step_num)

        self.reset_last_accessed()


class GameRunnerInitializationParams(object):

    def __init__(self, config):
        self.model_init_params = AgentModelInitializationParams()
        self.model_init_params.set_grid_width(100) \
            .set_grid_height(100) \
            .set_starting_model_time(datetime.timedelta())
        if 'termination' in config:
            self.model_init_params.set_termination(config['termination'])
        if 'logging' in config:
            self.model_init_params.set_logging(config['logging'])
        if 'minutes_per_step' in config:
            self.model_init_params.set_minutes_per_step(config['minutes_per_step'])
        if 'priorities' in config:
            self.model_init_params.set_priorities(config['priorities'])
        if 'location' in config:
            self.model_init_params.set_location(config['location'])
        self.model_init_params.set_config(config)
        if (config['single_agent'] == 1):
            self.model_init_params.set_single_agent(1)
        self.agent_init_recipe = BaseLineAgentInitializerRecipe(config)


class GameRunnerManager(object):
    """Manages all gamerunner objects held by this instance of the application.

    Attributes
    ----------
    DEFAULT_TIMEOUT_INTERVAL : int
         default value for timeout_interval
    DEFAULT_CLEANUP_MAX_INTERVAL : int
        default value for max_interval
    cleanup_thread : Thread
        worker thread to cleanup GameRunner objects which have timed out
    timeout_interval: int
        maximum time in seconds between cleanup thread runs
    max_interval: int
        seconds until GameRunner timesout and gets cleaned up
    game_runners : dict
        dictionary containing GameRunner's indexed by user id's

    """

    DEFAULT_TIMEOUT_INTERVAL = 120  # seconds
    DEFAULT_CLEANUP_MAX_INTERVAL = 10  # seconds

    def __init__(self, timeout_interval=None,
                 cleanup_max_interval=None):
        self.game_runners = {}

        if timeout_interval:
            self.timeout_interval = timeout_interval
        else:
            self.timeout_interval = self.DEFAULT_TIMEOUT_INTERVAL

        if cleanup_max_interval:
            self.cleanup_max_interval = cleanup_max_interval
        else:
            self.cleanup_max_interval = self.DEFAULT_CLEANUP_MAX_INTERVAL

        # thread will not end if it runs during unit test
        self.start_cleanup_thread()

    def start_cleanup_thread(self):
        """Starts a cleanup thread to remove game_runners
        that have timed out.  Should generally only be called
        internally or during test
        """

        # close existing cleanup thread if exists
        self.stop_cleanup_thread()

        def cleanup_at_interval():
            self.clean_up_inactive()
            new_interval = self.get_next_timeout()
            self.cleanup_thread = threading.Timer(
                new_interval, cleanup_at_interval)
            self.cleanup_thread.start()

        def close():
            print("Closing cleanup thread..")
            self.cleanup_thread.cancel()
            self.cleanup_thread.join()
            print("Cleanup thread closed.")
            self.save_all(allow_repeat_save=False)

        handler_partial = register_exit_handler(close)
        self.cleanup_thread = threading.Timer(
            self.cleanup_max_interval, cleanup_at_interval)
        self.cleanup_thread.start()
        self._handler_partial = handler_partial

    def stop_cleanup_thread(self):
        """For testing purposes, provides a method to close
        a cleanup thread explicitly after starting it
        """
        if hasattr(self, "_handler_partial"):
            self._handler_partial()
            remove_exit_handler(self._handler_partial)

    def new_game(self, user, game_runner_init_params):
        """Create a new game and add it to internal game_runners dict.
        If the user already holds a game instance, it is saved, if needed and removed.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user requesting the new game.
        game_runner_init_params : simoc_server.game_runner.GameRunnerInitializationParams
            initialization parameters for the new game
        """
        game_runner = GameRunner.from_new_game(user, game_runner_init_params)
        self._add_game_runner(user, game_runner)

    def load_game(self, user, saved_game):
        """Load a game and add it to the internal game_runners dict.
        If the user already holds a game instance, it is saved, if needed and removed.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user requesting to game, to be validated as the owner of the save by
            the GameRunner on initialization.
        saved_game : simoc_server.database.db_model.SavedGame
            The saved game to load.
        """
        game_runner = GameRunner.load_from_saved_game(user, saved_game)
        self._add_game_runner(saved_game.user, game_runner)

    def save_all(self, allow_repeat_save=True):
        """Save all currently active game_runners.

        Parameters
        ----------
        allow_repeat_save : bool, optional
            Allow a save if one already exists for the current step. Default - True.
        """
        for user in self.game_runners.keys():
            self.save_game(user, allow_repeat_save=allow_repeat_save)

    def save_game(self, user, save_name=None, allow_repeat_save=True):
        """Save the currently active game for the given user.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            Description
        save_name : None, optional
            A name to give the save, if None, automatically generated.
        allow_repeat_save : bool, optional
            Allow a save if one already exists for the current step. Default - True.

        Raises
        ------
        GameNotFoundException
            If there is no active game for the provided user.
        """
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
        """Get the game runner for the provided user.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user to get the associated game runner for.

        Returns
        -------
        GameRunner, NoneType
            Returns the game runner for the associated user if it exists,
            otherwise returns None
        """
        try:
            if isinstance(user, User):
                return self.game_runners[user.id]
            else:
                user_id = user
                return self.game_runners[user_id]
        except KeyError:
            return None

    def get_step(self, user, step_num=None):
        """Get the step number requested for the given user.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user requesting the step.
        step_num : int, optional
            The step number to get, must be greater than the current step number
            of the model.  If None, returns the next step.

        Returns
        -------
        dict
            A dictionary containing the internal state of the agent model
            at the requested step.

        Raises
        ------
        GameNotFoundException
            If there is no active game for the provided user.
        """
        game_runner = self.get_game_runner(user)
        if game_runner is None:
            raise GameNotFoundException()
        game_runner.step_to(step_num, False)
        step_data = ModelRecord.query \
            .filter_by(step=step_num) \
            .filter_by(user_id=user.id) \
            .first()
        response = step_data.get_data()
        response['agent_type_counters'] = [i.get_data() for i in step_data.agent_type_counters]
        response['storage_capacities'] = [i.get_data() for i in step_data.storage_capacities]
        return response

    def get_step_to(self, user, step_num=None):
        game_runner = self.get_game_runner(user)
        if game_runner is None:
            raise GameNotFoundException()
        game_runner.step_to(step_num, False)

    def ping(self, user):
        """Updates time when game runner was last accessed for the given
        user, preventing it from being removed during cleanup. Useful
        if the game is paused and no longer requesting steps.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user who is pinging the server
        """
        game_runner = self.get_game_runner(user)
        if game_runner is None:
            raise GameNotFoundException()
        game_runner.ping()

    def _add_game_runner(self, user, game_runner):
        """Adds the given game runner to self.game_runners and associates
        it with the given user.  If the user already holds a game instance,
        it is saved, if needed and removed.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user to add the game runner for
        game_runner : GameRunner
            The game runner to add
        """
        old_game = self.get_game_runner(user)
        if old_game is not None:
            self.save_game(user, allow_repeat_save=False)

        self.game_runners[user.id] = game_runner

    def _autosave_name(self):
        """Generates an autosave name using the format "Autosave <current_utc_datetime>"

        Returns
        -------
        str
            An automatically generated auto save name.
        """
        return "{}_{}".format(
            "Autosave",
            datetime.datetime.utcnow())

    def clean_up_inactive(self):
        """Cleans up all sessions that have timed out, used by the internal
        cleanup thread at an interval.
        """
        marked_for_cleanup = []
        for user_id, game_runner in self.game_runners.items():
            if (game_runner.seconds_since_last_accessed > self.timeout_interval):
                marked_for_cleanup.append(user_id)

        for user_id in marked_for_cleanup:
            try:
                app.logger.info("Cleaning up save game for user with id {}".format(user_id))
                self.save_game(user_id, allow_repeat_save=False)
                del self.game_runners[user_id]
            except KeyError as e:
                app.logger.error("Session for user '{}' removed before it could be cleaned up."
                                 .format(user_id))
            except Exception as e:
                app.logger.error("Unknown exception occured in game manager cleanup.")
                traceback.print_exc()

    def get_next_timeout(self):
        """Get the minimum duration to the next timeout, or TIMOUT_INTERVAL
        if no game runner's exist.

        Returns
        -------
        int or float
            the time till the next timeout given the current state
        """
        next_timeouts = [self.timeout_interval - runner.seconds_since_last_accessed
                         for runner in self.game_runners.values()]
        return max(0, min([self.timeout_interval] + next_timeouts))
