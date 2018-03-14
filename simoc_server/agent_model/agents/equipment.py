from simoc_server.agent_model.agents.core import BaseAgent
import datetime


class Equipment(BaseAgent):
    _agent_type_name = "default_equipment"

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        # self, name, default_value=None, _type=None, is_client_attr=True, is_persisted_attr=True
        #self.power_usage = kwargs.get("power_usage", 0.0)
        self.power_grid = kwargs.get("power_grid", None)
        self.efficiency = kwargs.get("efficiency", 100.0)

    def step(self):
        pass


class PowerModule(Equipment):
    _agent_type_name = "power_module"

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.structure = kwargs.get("structure", None)
        self.status = kwargs.get("status", "online")

        ### Variables for the grid
        self.power_storage_capacity = kwargs.get("power_storage_capacity", 13.0)
        self.power_usage = kwargs.get("power_usage", .002)  # need to get from structure. power consumed
        self.power_output_capacity = kwargs.get("power_output_capacity", 5.0)
        self.power_charge = kwargs.get("power_charge", 0.0)
        self.power_production = kwargs.get("power_production", .25) # will be calculated via solar panel count

        #self._attr(name="power_storage_capacity", default_value=kwargs.get("power_storage_capacity", 13.0), _type=None, is_client_attr=True, is_persisted_attr=True)
        #self._attr(name="power_usage", default_value=kwargs.get("power_usage", .002), _type=None, is_client_attr=True, is_persisted_attr=True) # need to get from structure. power consumed
        #self._attr(name="power_output_capacity", default_value=kwargs.get("power_output_capacity", 5.0), _type=None, is_client_attr=True, is_persisted_attr=True)
        #self._attr(name="power_charge", default_value=kwargs.get("power_charge", 0.0), _type=None, is_client_attr=True, is_persisted_attr=True)
        #self._attr(name="power_production", default_value=kwargs.get("power_production", .25), _type=None, is_client_attr=True,
        #           is_persisted_attr=True)

    def step(self):
        if self.power_grid is None:
            self.power_charge += (self.power_production - self.power_usage)
        else:
            self.power_charge += (self.power_production - self.power_usage)

    def set_power_grid(self, power_grid):
        self.power_grid = power_grid


## My code to test equipment agent functionality
"""
if __name__ == '__main__':
    from simoc_server.agent_model import AgentModel, AgentModelInitializationParams, BaseLineAgentInitializerRecipe
    from simoc_server.agent_model.agents import PowerStation

    default_model_params = AgentModelInitializationParams()
    (default_model_params.set_grid_width(100)
     .set_grid_height(100)
     .set_starting_model_time(datetime.timedelta()))
    default_agent_init_recipe = BaseLineAgentInitializerRecipe()

    model = AgentModel(init_params=default_model_params )
    print("model total storage capacity " + str(model.power_storage_capacity))
    print("model total charge " + str(model.power_charge))
    print("model total usage " + str(model.power_usage))
    print("model total output " + str(model.power_output_capacity))
    print("model total production " + str(model.power_production))

    equipment = PowerModule(model)
    power_station = PowerStation(model)
    running = True
    step = 0

    while running:
        print("step number" + str(step))
        print("power usage in kw:" + str(model.power_usage))
        print("power charge in kw:" + str(model.power_charge))
        print("power capacity in kwh:" + str(model.power_storage_capacity))
        print("power output capacity kw:" + str(model.power_output_capacity))
        print("power production kw:" + str(model.power_production))
        model.step()
        step += 1
        if step > 100 :
            running = False
"""