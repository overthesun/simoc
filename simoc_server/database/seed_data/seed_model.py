from . import util
from collections import OrderedDict
from simoc_server.database.db_model import AgentModelParam, GlobalModelConstant



def seed():
    params = gen_params()
    global_constants = gen_globals()

    util.add_all(params)
    util.add_all(global_constants)

def gen_params():
    def create_param(name, value, description, details=None):
        return AgentModelParam(name=name, value=str(value),
            value_type=str(type(value).__name__), description=description,
            details=details)

    data = OrderedDict()

    data["minutes_per_step"] = create_param(name="minutes_per_step", \
        value=60, description="Number of minutes per 1 model step.", details="min/step")
    data["meters_per_grid_unit"] = create_param(name="meters_per_grid_unit", \
        value=1, description="Number of square meters in 1 grid unit.", details="m^2")

    data["initial_oxygen"] = create_param(name="initial_oxygen", \
        value=21.22, description="Initial oxygen in the system.", details="kPa")
    data["initial_carbon_dioxide"] = create_param(name="initial_carbon_dioxide",
        value=0.041, description="Initial carbon dioxide in the system.", details="kPa")
    data["initial_nitrogen"] = create_param(name="initial_nitrogen",
        value=79.11, description="Initial nitrogen in the system.", details="kPa")
    data["initial_argon"] = create_param(name="initial_argon",
        value=0.94, description="Initial argon in the system.", details="kPa")
    data["initial_water"] = create_param(name="initial_water",
        value=10000.0, description="Initial water in the system.", details="kg")
    data["initial_waste_water"] = create_param(name="initial_waste_water",
        value=0.0, description="Initial waste water in the system.", details="kg")
    data["initial_temp"] = create_param(name="initial_temp",
        value=293.0, description="Initial temperature of the system.", details="K")


    return data

def gen_globals():
    data = OrderedDict()

    def create_global(name, value, description, details=None):
        return GlobalModelConstant(name=name, value=value, 
            value_type=str(type(value).__name__), description=description, details=details)

    data["globals_gas_constant"] = create_global("gas_constant",  .0083145,
        "Ideal gas constant, denoted R. Uses kL, equiv. to meters^3", details="(kL * kPa)/(mol * K)")
    data["globals_oxygen_molar_mass"] = create_global("oxygen_molar_mass", 31.998, 
        "The molar mass of oxygen", details="g/mol")
    data["globals_carbon_dioxide_molar_mass"] = create_global("carbon_dioxide_molar_mass", 44.009, 
        "The molar mass of carbon dioxide", details="g/mol")
    data["globals_nitrogen_molar_mass"] = create_global("nitrogen_molar_mass", 28.014, 
        "The molar mass of nitrogen", details="g/mol")
    data["globals_argon_molar_mass"] = create_global("argon_molar_mass", 39.948, 
        "The molar mass of argon", details="g/mol")
    data["globals_water_molar_mass"] = create_global("water_molar_mass", 18.015, 
        "The molar mass of water", details="g/mol")

    return data