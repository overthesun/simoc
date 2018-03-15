from simoc_server.agent_model.agents.core import BaseAgent

#from simoc_server.agent_model import AgentModel


class Equipment(BaseAgent):
    _agent_type_name = "default_equipment"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #attributes: __attr() not sure why using thiat vs get
        # self, name, default_value=None, _type=None, is_client_attr=True, is_persisted_attr=True
        self.model = kwargs.get("model")
        self.name = kwargs.get("name","equipment")
        self.power_usage = kwargs.get("power_usage", 0)
        self.power_grid = kwargs.get("power_grid", None)

    def step(self):
        pass


class PowerModule(Equipment):
    _agent_type_name = "power_module"
    print("New Power Module")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.power_grid = kwargs.get("power_grid", None)
        self.structure = kwargs.get("structure", None)
        ### Variables for the grid
        self.power_storage_capacity = kwargs.get("power_storage_capacity", 13)
        self.power_usage = kwargs.get("power_usage", .002)  # need to get from structure. power consumed
        self.power_output_capacity = kwargs.get("power_output_capacity", 5)
        self.power_charge = kwargs.get("power_charge", 0)
        self.power_production = kwargs.get("power_production", .25) # will be calculated via solar panel count

        self._attr(name="Power Module", default_value=kwargs.get("name", "Power Module"), _type=None,
                   is_client_attr=True, is_persisted_attr=True)
        self._attr(name="power_storage_capacity", default_value=kwargs.get("power_storage_capacity", 13), _type=None, is_client_attr=True, is_persisted_attr=True)
        self._attr(name="power_usage", default_value=kwargs.get("power_usage", .002), _type=None, is_client_attr=True, is_persisted_attr=True) # need to get from structure. power consumed
        self._attr(name="power_output_capacity", default_value=kwargs.get("power_output_capacity", 5), _type=None, is_client_attr=True, is_persisted_attr=True)
        self._attr(name="power_charge", default_value=kwargs.get("power_charge", 0), _type=None, is_client_attr=True, is_persisted_attr=True)
        self._attr(name="power_production", default_value=kwargs.get("power_production", .25), _type=None, is_client_attr=True,
                   is_persisted_attr=True)

    def step(self):
        if self.power_grid is None:
            self.power_charge += (self.power_usage + self.power_production)
        else:
            self.power_grid += (self.power_usage + self.power_production)

    def set_power_grid(self, power_grid):
        self.power_grid = power_grid



'''
## My code to test equipment agent functionality
if __name__ == '__main__':

    model = AgentModel(init_params=None)
    model.init_agents()
    print("model total power capacity " + str(model.total_power_capacity))
    print("model total charge " + str(model.total_power_charge))
    print("model total usage " + str(model.total_power_usage))
    print("model total output " + str(model.total_power_output))
    equipment = PowerModule(model=model)
    running = True
    step = 0
    while running:
        print("step number" + str(step))
        print("power usage in kw:" + str(equipment.power_usage))
        print("power charge in kw:" + str(equipment.power_charge))
        print("power capacity in kwh:" + str(equipment.power_storage_capacity))
        print("power output capacity kw:" + str(equipment.power_output_capacity))

        equipment.step()
        step += 1
        if step > 100 :
            running = False

'''