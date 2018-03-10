from simoc_server.agent_model.agents.core import BaseAgent
#from simoc_server.agent_model.agent_model import AgentModel


class Equipment(BaseAgent):
    _agent_type_name = "Equipment"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #attributes: __attr() not sure why using thiat vs get
        # self, name, default_value=None, _type=None, is_client_attr=True, is_persisted_attr=True
        self.model = kwargs.get("model")
        self.name = kwargs.get("name","equipment")
        self.power_usage = kwargs.get("usage", 0)
        self.power_grid = kwargs.get("power_grid", None)
        pass

    def step(self):
        pass


class PowerModule(Equipment):
    _agent_type_name = "Power_Module"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.structure = kwargs.get("structure", None)
        self.power_storage_capacity = kwargs.get("power_storage_capacity", 0)
        self.power_usage = kwargs.get("power_usage", .02)
        self.power_output_capacity = kwargs.get("power_output_capacity", 0)
        self.power_charge = kwargs.get("power_charge", 0)
        pass

    def step(self):
        pass

#if __name__ == '__main__':
    #equipment = Equipment(storage=150, usage=.5)
    #equipment.step()
    #print()
    #running = True
    #while running:
    #    running = False

#if __name__ == '__main__':
#    model = AgentModel.create_new(100,100)
#    equip = Equipment(model=model)
#    running = True
#    while running:
