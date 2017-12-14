import datetime
from .baseagent import BaseAgent
from .sprite_mappers import PlantSpriteMapper

class PlantAgent(BaseAgent):
    # TODO implement each plant and abstract this class

    __agent_type_name__ = "default_plant"
    __sprite_mapper__ = PlantSpriteMapper
    __persisted_attributes__ = ["status"]
    __client_attributes__ = ["status"]

    def init_new(self):
        self.status = "planted"
        # TODO find out how long plants take to grow
        self.grow_time = datetime.timedelta(days=30)
        # TODO find out how long plants live
        self.lifespan = datetime.timedelta(days=200)

        # TODO save time delta to database and load it back up
        self.planted_time_delta = self.model.get_timedelta_since_start()


    def step(self):
        if not hasattr(self, "planted_time_delta"):
            print("WARNING: PLANTED TIME DELTA NOT ADDED, NEED TO FIX THIS")
            self.planted_time_delta = self.model.get_timedelta_since_start()
        current_time_delta = self.model.get_timedelta_since_start()
        age = (current_time_delta - self.planted_time_delta)
        if age > self.grow_time:
            self.status = "grown"
        if age > self.lifespan:
            self.destroy(self)