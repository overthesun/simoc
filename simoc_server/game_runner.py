import threading
from simoc_server.agent_model import AgentModel
from simoc_server.serialize import AgentModelDTO

class GameRunner(object):
    __default_grid_size__ = (100, 100)

    def __init__(self, agent_model, step_buffer_size=10):
        self.agent_model = agent_model
        self.step_buffer_size = step_buffer_size
        self.step_thread = None
        self.step_buffer = {}

    @classmethod
    def load_from_state(cls, agent_model_state, step_buffer_size=10):
        agent_model = AgentModel(agent_model_state, \
            step_buffer_size=step_buffer_size)
        return GameRunner(agent_model)

    @classmethod
    def from_new_game(cls, step_buffer_size=10):
        grid_width = GameRunner.__default_grid_size__[0]
        grid_height = GameRunner.__default_grid_size__[1]
        agent_model = AgentModel(grid_width=grid_width, grid_height=grid_height)
        return GameRunner(agent_model, step_buffer_size=step_buffer_size)

    def get_step(self, step_num):
        self._step_to(step_num, False)
        return self._get_step_from_buffer(step_num)


    def _get_step_from_buffer(self, step_num):
        step = self.step_buffer[step_num]

        pruned_buffer = {}
        for n, step in self.step_buffer.items():
            if n > step_num:
                pruned_buffer[n] = step

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
