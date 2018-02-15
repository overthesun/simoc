import datetime

from simoc_server.agent_model.sprite_mappers import PlantSpriteMapper
from simoc_server.agent_model.agents.core import EnclosedAgent

class PlantAgent(EnclosedAgent):
    # TODO implement each plant and abstract this class

    _agent_type_name = "default_plant"
    _sprite_mapper = PlantSpriteMapper

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
            self.destroy()