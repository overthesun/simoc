import datetime

from simoc_server.agent_model.sprite_mappers import PlantSpriteMapper
from simoc_server.agent_model.agents.core import EnclosedAgent

class PlantAgent(EnclosedAgent):
    # TODO implement each plant and abstract this class

    _agent_type_name = "default_plant"
    _sprite_mapper = PlantSpriteMapper
    # TODO separate plants based on multiple or single harvest 
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
            self.structure.plants_ready += 1
        if age > self.lifespan:
            self.destroy()


class CabbageAgent(PlantAgent):
    _agent_type_name = "cabbage"

class CarrotAgent(PlantAgent):
    _agent_type_name = "carrot"

class ChardAgent(PlantAgent):
    _agent_type_name = "chard"

class CryBeanAgent(PlantAgent):
    _agent_type_name = "dry_bean"

class LettuceAgent(PlantAgent):
    _agent_type_name = "Lettuce"

class PeaAgent(PlantAgent):
    _agent_type_name = "pea"

class PeanutAgent(PlantAgent):
    _agent_type_name = "peanut"

class PepperAgent(PlantAgent):
    _agent_type_name = "pepper"

class RedBeetAgent(PlantAgent):
    _agent_type_name = "red_beet"

class RiceAgent(PlantAgent):
    _agent_type_name = "rice"

class SnapBeanAgent(PlantAgent):
    _agent_type_name = "snap_bean"

class SoybeanAgent(PlantAgent):
    _agent_type_name = "soybean"

class SpinachAgent(PlantAgent):
    _agent_type_name = "spinach"

class StrawberryAgent(PlantAgent):
    _agent_type_name = "strawberry"

class SweetPotatoAgent(PlantAgent):
    _agent_type_name = "sweet_potato"

class TomatoAgent(PlantAgent):
    _agent_type_name = "tomato"

class WheatAgent(PlantAgent):
    _agent_type_name = "wheat"

class WhitePotatoAgent(PlantAgent):
    _agent_type_name = "white_potato"
