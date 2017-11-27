import os
import unittest
import tempfile
import time
import threading

os.environ["DIAG_CONFIG_MODULE"] = "simoc_server.test_settings"

from simoc_server import db, app
from simoc_server.agent_model import AgentModel
from simoc_server.database.db_model import AgentModelState
from simoc_server.database.seed_data import seed
import simoc_server


class SimocServerTestCase(unittest.TestCase):

    def setUp(self):
        simoc_server.app.testing = True
        db.create_all()
        seed.seed()

    def tearDown(self):
        db.sessionmaker.close_all()
        # db.engine.dispose()
        db.drop_all()

    def testConcurrentBranching(self):
        snapshot_ind = 0
        def snapshot_at_step_1(agent_model_id, branch_ids):
            agent_model_state = AgentModelState.query.get(agent_model_id)
            agent_model = AgentModel(agent_model_state=agent_model_state)
            agent_model.step()
            snapshot = agent_model.snapshot()
            branch_ids.append(snapshot.snapshot_branch.id)
        orig_agent_model = AgentModel(grid_width=100, grid_height=100)
        snapshot = orig_agent_model.snapshot()
        model_state_id = snapshot.agent_model_state.id
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
                self.assertTrue(branch_ids[i] != branch_ids[j])



if __name__ == "__main__":
    unittest.main()