import threading
from simoc_server import db
from simoc_server.agent_model import AgentModel
from simoc_server.serialize import AgentModelDTO
from simoc_server.database import SavedGame

class GameRunner(object):
    __default_grid_size__ = (100, 100)

    def __init__(self, agent_model, user, step_buffer_size=10):
        self.agent_model = agent_model
        self.user = user
        self.step_buffer_size = step_buffer_size
        self.step_thread = None
        self.step_buffer = {}

    @classmethod
    def load_from_state(cls, agent_model_state, user, step_buffer_size=10):
        if agent_model_state is None:
            raise Exception("Got None for agent_model_state.")
        agent_model = AgentModel.load_from_db(agent_model_state)
        return GameRunner(agent_model, user, step_buffer_size=step_buffer_size)

    @classmethod
    def load_from_saved_game(cls, saved_game, step_buffer_size=10):
        agent_model_state = saved_game.agent_model_snapshot.agent_model_state
        user = saved_game.user
        return GameRunner.load_from_state(agent_model_state, user, step_buffer_size)

    @classmethod
    def from_new_game(cls, user, step_buffer_size=10):
        grid_width = GameRunner.__default_grid_size__[0]
        grid_height = GameRunner.__default_grid_size__[1]
        agent_model = AgentModel.create_new(100, 100)
        return GameRunner(agent_model, user, step_buffer_size=step_buffer_size)

    def save_game(self, save_name):
        agent_model_snapshot = self.agent_model.snapshot(commit=False)
        saved_game = SavedGame(user=self.user, agent_model_snapshot=agent_model_snapshot, name=save_name)
        db.session.add(saved_game)
        db.session.commit()
        return saved_game

    def get_step(self, step_num=None):
        if(step_num is None):
            step_num = self.agent_model.step_num + 1
        self._step_to(step_num, False)
        return self._get_step_from_buffer(step_num)


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
