import os
import unittest
import tempfile
import time
import threading
from simoc_server import db, app
from simoc_server.agent_model import AgentModel
from simoc_server.agent_model.agent_attribute_meta import AgentAttributeHolder
from simoc_server.agent_model.agents import BaseAgent
from simoc_server.agent_model.agents.agent_name_mapping import _add_agent_class_to_mapping
from simoc_server.database.db_model import AgentModelState, User, AgentType
from simoc_server.database.seed_data import seed
from simoc_server.game_runner import GameRunner

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

        #print(branch_ids)
        for i in range(len(branch_ids)):
            for j in range(i+1, len(branch_ids)):
                self.assertNotEqual(branch_ids[i], branch_ids[j])


    def testTimeDelta(self):
        agent_model = AgentModel.create_new(100, 100)
        for i in range(100):
            agent_model.step()
            #print(agent_model.model_time)
        delta = agent_model.model_time
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

    def testPersistedAttributes(self):
        # persisted attributes should be saved and loaded to/from the database
        class AgentA(BaseAgent):
            _agent_type_name = "agent_a"

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._attr("agent_a_attribute", 16, is_persisted_attr=True)

        # add agent type data to database
        agent_a_type = AgentType(name="agent_a")
        db.session.add(agent_a_type)
        db.session.commit()

        # add agent to agent_name_mappings
        _add_agent_class_to_mapping(AgentA)

        # create game
        test_user = self.__class__.test_user
        game_runner = GameRunner.from_new_game(test_user)

        # create agent
        agent_model = game_runner.agent_model
        agent_a = AgentA(agent_model)

        # make sure attributes are set properly
        self.assertTrue(hasattr(agent_a, "agent_a_attribute"))
        self.assertEqual(agent_a.agent_a_attribute, 16)

        # add agent to model
        agent_model.add_agent(agent_a)
        game_runner.get_step(1)

        # save game
        saved_game = game_runner.save_game("test")

        # load game
        game_runner_2 = GameRunner.load_from_saved_game(saved_game)

        # get agents
        loaded_agent_model = game_runner_2.agent_model
        loaded_agents = loaded_agent_model.get_agents()
        # make sure agent exists and only exists once
        matching_agents = list(filter(lambda x: x.unique_id == agent_a.unique_id, loaded_agents))
        self.assertTrue(len(matching_agents) == 1)

        # make sure agent attribute loaded correctly
        loaded_agent = matching_agents[0]
        self.assertEqual(loaded_agent.agent_a_attribute, 16)


if __name__ == "__main__":
    unittest.main()