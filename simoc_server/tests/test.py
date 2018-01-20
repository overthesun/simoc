import os
import unittest
import tempfile
import time
import threading
from simoc_server import db, app
from simoc_server.agent_model import AgentModel
from simoc_server.database.db_model import AgentModelState, User
from simoc_server.database.seed_data import seed
from simoc_server.game_runner import GameRunner
import simoc_server


class SimocServerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()
        seed.seed()

        cls.test_user = User(username="bob")
        cls.test_user.set_password("test_pass")
        db.session.add(cls.test_user)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.sessionmaker.close_all()
        # db.engine.dispose()
        db.drop_all()

    def testConcurrentBranching(self):
        snapshot_ind = 0
        def snapshot_at_step_1(agent_model_id, branch_ids):
            agent_model_state = AgentModelState.query.get(agent_model_id)
            agent_model = AgentModel.load_from_db(agent_model_state)
            agent_model.step()
            snapshot = agent_model.snapshot()
            branch_ids.append(snapshot.snapshot_branch.id)
        orig_agent_model = AgentModel.create_new(100, 100)
        orig_snapshot_1 = orig_agent_model.snapshot()
        orig_agent_model.step()
        orig_snapshot_2 = orig_agent_model.snapshot()
        model_state_id = orig_snapshot_2.agent_model_state.id
        num_branches = 10
        threads = []
        branch_ids = []
        for i in range(num_branches):
            t=threading.Thread(target=snapshot_at_step_1, args=(model_state_id,branch_ids))
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()

        print(branch_ids)
        for i in range(len(branch_ids)):
            for j in range(i+1, len(branch_ids)):
                self.assertNotEqual(branch_ids[i], branch_ids[j])


    def testTimeDelta(self):
        agent_model = AgentModel.create_new(100, 100)
        for i in range(100):
            agent_model.step()
            print(agent_model.get_timedelta_since_start())
        delta = agent_model.get_timedelta_since_start()
        self.assertEqual(delta.days, 4)

    def testSpaceConversion(self):
        agent_model = AgentModel.create_new(100, 100)
        m1 = agent_model.grid_units_to_meters(10)
        self.assertEqual(m1, 10)
        m2 = agent_model.grid_units_to_meters((20, 60))
        self.assertEqual(m2, (20, 60))

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

if __name__ == "__main__":
    unittest.main()