import unittest
from simoc_server import db
from simoc_server.tests.test_util import setup_db, clear_db
from simoc_server.database.db_model import User
from simoc_server.game_runner import GameRunner

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

    @classmethod
    def tearDownClass(cls):
        clear_db()


    def testSaveGame(self):
        test_user = self.__class__.test_user
        game_runner = GameRunner.from_new_game(test_user)

        buffer_size = game_runner.step_buffer_size

        game_runner.get_step(1)
        game_runner.get_step(2)
        game_runner.get_step(3)

        saved_game = game_runner.save_game("test")

        game_runner_2 = GameRunner.load_from_saved_game(saved_game)
        self.assertEqual(game_runner_2.agent_model.step_num, 3 + buffer_size)