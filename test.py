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
            previous_snap_ids.append(snapshot.previous_snapshot.id)
        orig_agent_model = AgentModel(grid_width=100, grid_height=100)
        orig_snapshot = orig_agent_model.snapshot()
        model_state_id = orig_snapshot.agent_model_state.id
        num_branches = 10
        threads = []
        previous_snap_ids = []
        for i in range(num_branches):
            t=threading.Thread(target=snapshot_at_step_1, args=(model_state_id,previous_snap_ids))
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()

        print(previous_snap_ids)
        for i in range(len(previous_snap_ids)):
            self.assertTrue(previous_snap_ids[i] == orig_snapshot.id)



if __name__ == "__main__":
    unittest.main()