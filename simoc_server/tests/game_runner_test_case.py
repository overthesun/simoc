import unittest
import time

from simoc_server import db, app
from simoc_server.tests.test_util import setup_db, clear_db
from simoc_server.database.db_model import User
from simoc_server.game_runner import (GameRunnerManager,
    GameRunner, GameRunnerInitializationParams)

class GameRunnerTestCase(unittest.TestCase):

    """Test the game runner.
    """

    @classmethod
    def setUpClass(cls):
        setup_db()
        cls.test_user = User(username="bob")
        cls.test_user.set_password("test_pass")
        db.session.add(cls.test_user)
        db.session.commit()

        cls.default_game_runner_init_params = GameRunnerInitializationParams(None, None, 
            None, None, None)

    @classmethod
    def tearDownClass(cls):
        clear_db()


    def testSaveGame(self):
        test_user = self.__class__.test_user
        game_runner = GameRunner.from_new_game(test_user, 
            self.default_game_runner_init_params)

        buffer_size = game_runner.step_buffer_size

        game_runner.get_step(1)
        game_runner.get_step(2)
        game_runner.get_step(3)

        saved_game = game_runner.save_game("test")

        game_runner_2 = GameRunner.load_from_saved_game(test_user, saved_game)
        self.assertEqual(game_runner_2.agent_model.step_num, 3 + buffer_size)

    def testGameRunnerManagerCleanup(self):
        """Test the game runner manager cleanup thread.
        This test case makes assumptions about its own
        execution time, namely it assumes that certain
        statements will execute in less time than
        the time left before the game_runner instance times
        out
        """
        # set low interval for timeout to make test faster
        # can't set too low so due to non-deterministic
        # execution
        timeout_interval = 6
        # set low interval for cleanup thread to ensure
        # it runs many times
        cleanup_max_interval = .1

        game_runner_manager = GameRunnerManager(timeout_interval=timeout_interval,
            cleanup_max_interval=cleanup_max_interval)
        game_runner_manager.start_cleanup_thread()

        try:
            game_runner_manager.new_game(self.__class__.test_user,
                self.__class__.default_game_runner_init_params)

            create_time = time.time()
            game = game_runner_manager.get_game_runner(self.__class__.test_user)

            duration = time.time() - create_time

            self.assertIsNotNone(game, msg="GameRunner got cleaned up or was never created "
                "before expected timed out. This could happen if the sleep function runs "
                "longer than it was supposed to or if this code takes an unreasonably long "
                "time to execute even if everything goes right. "
                "Duration is {}s timeout interval is {}s".format(duration, timeout_interval))

            time.sleep(timeout_interval/2.0)

            game = game_runner_manager.get_game_runner(self.__class__.test_user)

            duration = time.time() - create_time

            self.assertIsNotNone(game, msg="GameRunner got cleaned up or was never created "
                "before expected timed out. This could happen if the sleep function runs "
                "longer than it was supposed to or if this code takes an unreasonably long "
                "time to execute even if everything goes right. "
                "Duration is {}s timeout interval is {}s".format(duration, timeout_interval))

            # sleep until timeout
            time.sleep(timeout_interval/2.0 + 1)

            game = game_runner_manager.get_game_runner(self.__class__.test_user)

            duration = time.time() - create_time

            self.assertIsNone(game, msg="GameRunner manager was not cleaned up after "
                "expected timeout. This could happen if the sleep function runs "
                "for less time than it was supposed to even if everything goes right. "
                "Duration is {}s timeout interval is {}s".format(duration, timeout_interval))

        finally:
            # ensure cleanup thread is closed even
            # if test fails
            app.logger.info("stopping test cleanup thread")
            game_runner_manager.stop_cleanup_thread()