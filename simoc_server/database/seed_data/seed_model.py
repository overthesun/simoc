from . import util
from collections import OrderedDict
from simoc_server.database.db_model import AgentModelParam



def seed():
    params = gen_params()

    util.add_all(params)

def gen_params():
    def create_param(name, value, description, units=None):
        return AgentModelParam(name=name, value=str(value),
            value_type=str(type(value).__name__), description=description,
            units=units)

    data = OrderedDict()

    data["minutes_per_step"] = create_param(name="minutes_per_step", \
        value=60, description="Number of minutes per 1 model step.", units="min/step")
    data["meters_per_grid_unit"] = create_param(name="meters_per_grid_unit", \
        value=1, description="Number of square meters in 1 grid unit.", units="m^2")

    data["initial_oxygen"] = create_param(name="initial_oxygen", \
        value=21.22, description="Initial oxygen in the system.", units="kPa")
    data["initial_carbon_dioxide"] = create_param(name="initial_carbon_dioxide",
        value=0.041, description="Initial carbon dioxide in the system.", units="kPa")
    data["initial_nitrogen"] = create_param(name="initial_nitrogen",
        value=79.11, description="Initial nitrogen in the system.", units="kPa")
    data["initial_argon"] = create_param(name="initial_argon",
        value=0.94, description="Initial argon in the system.", units="kPa")
    data["initial_water"] = create_param(name="initial_water",
        value=10000.0, description="Initial water in the system.", units="kg")
    data["initial_waste_water"] = create_param(name="initial_waste_water",
        value=0.0, description="Initial waste water in the system.", units="kg")
    data["initial_temp"] = create_param(name="initial_temp",
        value=293.0, description="Initial temperature of the system.", units="K")


    return data
