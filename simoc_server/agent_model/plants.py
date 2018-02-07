import datetime
from .baseagent import BaseAgent
from .sprite_mappers import PlantSpriteMapper

class PlantAgent(BaseAgent):
    # TODO implement each plant and abstract this class

    __agent_type_name__ = "default_plant"
    __sprite_mapper__ = PlantSpriteMapper
    __persisted_attributes__ = ["status"]
    __client_attributes__ = ["status"]

    # TODO find out how long plants take to grow
    grow_time = datetime.timedelta(days=30)
    # TODO find out how long plants live
    lifespan = datetime.timedelta(days=200)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attr("status", "planted", is_client_attr=True, is_persisted_attr=True)


    def step(self):
        current_time_delta = self.model.model_time
        age = (current_time_delta - self.model_time_created)
        if age > self.grow_time:
            self.status = "grown"
        if age > self.lifespan:
            self.destroy(self)