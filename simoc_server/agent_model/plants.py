import datetime
from .baseagent import BaseAgent

class Plant(BaseAgent):
    # TODO implement each plant and abstract this class

    __agent_type_name__ = "default_plant"

    def init_new(self):
        self.status = "planted"
        # TODO find out how long plants take to grow
        self.grow_time = datetime.timedelta(days=30)
        # TODO find out how long plants live
        self.lifespan = datetime.timedelta(days=200)

        self.planted_time_delta = self.model.get_timedelta_since_start()


    def step(self):
        current_time_delta = self.model.get_timedelta_since_start()
        age = (current_time_delta - planted_time_delta)
        if age > self.grow_time:
            self.status = "grown"
        if age > self.lifespan:
            self.model.remove(self)