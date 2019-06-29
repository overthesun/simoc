import datetime
import threading
import time
import traceback
from uuid import uuid4

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
from simoc_server.front_end_routes import parse_step_data


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
        self.game_id = str(uuid4().hex[:8])
        self.start_time = int(time.time())
        self.user = user
        self.agent_model = agent_model
        self.agent_model.user_id = self.user.id
        self.step_thread = None
        self.last_accessed = None
        self.last_saved_step = last_saved_step
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

    def step_to(self, step_num, buffer_size):
        """Run the agent model to the requested step.

        Parameters
        ----------
        step_num : int
            Step number to run the model to.
        buffer_size : int
            Size of the buffer used to batch the database updates
        """
        def _save_records(model_records, agent_type_counts, storage_capacities, step_records):
            for record in model_records + agent_type_counts + storage_capacities + step_records:
                record['start_time'] = self.start_time
                record['game_id'] = self.game_id
            if len(model_records) > 0:
                db.session.execute(ModelRecord.__table__.insert(), model_records,)
            if len(agent_type_counts) > 0:
                db.session.execute(AgentTypeCountRecord.__table__.insert(), agent_type_counts,)
            if len(storage_capacities) > 0:
                db.session.execute(StorageCapacityRecord.__table__.insert(), storage_capacities,)
            if len(step_records) > 0:
                db.session.execute(StepRecord.__table__.insert(), step_records,)
            db.session.commit()

        def step_loop(agent_model):
            model_records_buffer = []
            agent_type_counts_buffer = []
            storage_capacities_buffer = []
            while agent_model.step_num <= step_num and not agent_model.is_terminated:
                agent_model.step()
                model_record, agent_type_counts, storage_capacities = agent_model.get_step_logs()
                model_records_buffer.append(model_record)
                agent_type_counts_buffer += agent_type_counts
                storage_capacities_buffer += storage_capacities
                if agent_model.step_num % buffer_size == 0:
                    _save_records(model_records_buffer,
                                  agent_type_counts_buffer,
                                  storage_capacities_buffer,
                                  agent_model.step_records_buffer)
                    model_records_buffer = []
                    agent_type_counts_buffer = []
                    storage_capacities_buffer = []
                    agent_model.step_records_buffer = []
            _save_records(model_records_buffer,
                          agent_type_counts_buffer,
                          storage_capacities_buffer,
                          agent_model.step_records_buffer)

        step_loop(self.agent_model)
        self.reset_last_accessed()


class GameRunnerInitializationParams(object):

    def __init__(self, config):
        self.model_init_params = AgentModelInitializationParams()
        self.model_init_params.set_grid_width(100) \
            .set_grid_height(100) \
            .set_starting_model_time(datetime.timedelta())
        if 'termination' in config:
            self.model_init_params.set_termination(config['termination'])
        if 'minutes_per_step' in config:
            self.model_init_params.set_minutes_per_step(config['minutes_per_step'])
        if 'priorities' in config:
            self.model_init_params.set_priorities(config['priorities'])
        if 'location' in config:
            self.model_init_params.set_location(config['location'])
        self.model_init_params.set_config(config)
        if 'single_agent' in config and config['single_agent'] == 1:
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

    DEFAULT_TIMEOUT_INTERVAL = 300  # seconds
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

    def get_last_steps(self, user, game_id, num_last_steps=1):
        """Get the the last N steps for the given user and the game.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user requesting the step.
        game_id : str
            A string Id of the game to retrieve the step from; Generated by the GameRunner object.
        num_last_steps : int
            The number of the last steps to get.

        Returns
        -------
        list
            A list containing the internal states of the agent model
            at the requested steps.

        """
        steps = ModelRecord.query \
            .filter_by(user_id=user.id) \
            .filter_by(game_id=game_id) \
            .order_by(ModelRecord.step_num.desc()) \
            .limit(num_last_steps) \
            .all()
        if len(steps) > 0:
            return [parse_step_data(step_data) for step_data in steps]
        else:
            return []

    def get_steps(self, user, game_id, start_step_num=0, stop_step_num=0):
        """Get the step range requested for the given user and the game.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user requesting the step.
        game_id : str
            A string Id of the game to retrieve the step from; Generated by the GameRunner object.
        start_step_num : int
            The starting step number of the range.
        stop_step_num : int
            The final step number of the range.

        Returns
        -------
        list
            A list containing the internal states of the agent model
            at the requested steps.

        """
        steps = ModelRecord.query \
            .filter_by(user_id=user.id) \
            .filter_by(game_id=game_id) \
            .filter(ModelRecord.step_num >= start_step_num) \
            .filter(ModelRecord.step_num <= stop_step_num) \
            .all()
        if len(steps) > 0:
            return [parse_step_data(step_data) for step_data in steps]
        else:
            return []

    def get_step(self, user, game_id, step_num=None,parse_filters=["agent_type_counters","storage_capacities"]):
        """Get the step number requested for the given user and the game.

        Accessed from front end using route get_step() in views.py

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user requesting the step.
        game_id : str
            A string Id of the game to retrieve the step from; Generated by the GameRunner object.
        step_num : int, optional
            The step number to get. If None, returns the last step.

        Returns
        -------
        dict
            A dictionary containing the internal state of the agent model
            at the requested step.
        """
        step_data = ModelRecord.query \
            .filter_by(user_id=user.id) \
            .filter_by(game_id=game_id)
        if step_num is None:
            step_data = step_data \
                .order_by(ModelRecord.step_num.desc()) \
                .limit(1)
        else:
            step_data = step_data.filter_by(step_num=step_num)
        step_data = step_data.first()
        if step_data is None:
            return {},step_data
        else:
            return parse_step_data(step_data,parse_filters),step_data

    def get_step_to(self, user, step_num=None, buffer_size=10):
        """Run the agent model to the requested step.

        Parameters
        ----------
        user : simoc_server.database.db_model.User
            The user requesting the step.
        step_num : int
            Step number to run the model to.
        buffer_size : int
            Size of the buffer used to batch the database updates.

        Raises
        ------
        GameNotFoundException
            If there is no active game for the provided user.
        """
        game_runner = self.get_game_runner(user)
        if game_runner is None:
            raise GameNotFoundException()
        game_runner.step_to(step_num, buffer_size)

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

    @staticmethod
    def _autosave_name():
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
            if game_runner.seconds_since_last_accessed > self.timeout_interval:
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
                app.logger.error("Unknown exception occurred in game manager cleanup.")
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
