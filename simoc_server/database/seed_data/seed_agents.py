from . import util
from collections import OrderedDict
from simoc_server.database.db_model import AgentType, AgentTypeAttribute


UNITLESS = "unknown"

def seed():
    human_data = gen_human()
    plant_data = gen_plants()
    structure_data = gen_structures()
    misc = gen_misc()

    util.add_all(human_data)
    util.add_all(plant_data)
    util.add_all(structure_data)
    util.add_all(misc)

def gen_misc():
    data = OrderedDict()
    data["enclosed_agent_type"] = AgentType(name="enclosed_agent")
    data["atmosphere"] = AgentType(name="atmosphere")
    data["plumbing_system"] = AgentType(name="plumbing_system")
    data["stored_mass"] = AgentType(name="stored_mass")
    data["stored_food"] = AgentType(name="stored_food")
    return data

def gen_human():
    data = OrderedDict()
    data["human_agent_type"] = AgentType(name="human")

    _type = data["human_agent_type"]

    age_units = "years"
    mass_usage_units = "Kg/CrewMember*d"
    gas_units = "kPa"
    food_energy_units = "kJ"


    # specifies age limits for earth-to-colony humans
    data["human_min_arrival_age"] = create_agent_type_attr(
        _type, "min_arrival_age", 21.0, units=age_units,
        description="Minimum expected arrival age of a human coming"
            "from earth")
    data["human_max_arrival_age"] = create_agent_type_attr(
        _type, "max_arrival_age", 50.0, units=age_units,
        description="Maximum expected arrival age of a human coming"
            "from earth")

    # biometrics

    # todo add normal distribution
    data["human_initial_mass_mean"] = create_agent_type_attr(
        _type, "initial_mass_mean", 82.0, units="kg", description="Mean initial mass of a human.")
    data["human_initial_mass_std"] = create_agent_type_attr(
        _type, "initial_mass_std", 0.0, units="", description="Standard deviation of initial mass of a human.")
    data["human_initial_age_mean"] = create_agent_type_attr(
        _type, "initial_age_mean", 40.0, units="years", description="Mean initial age of a human.")
    data["human_initial_age_std"] = create_agent_type_attr(
        _type, "initial_age_std", 0.0, units="", description="Standard deviation of initial age of a human.")
    data["human_initial_height_mean"] = create_agent_type_attr(
        _type, "initial_height_mean", 1.829, units="meters", description="Mean intitial height of a human.")
    data["human_initial_height_std"] = create_agent_type_attr(
        _type, "initial_height_std", 0.0, units="", description="Standard deviation of initial height of a human.")

    # food
    data["human_required_food_energy"] = create_agent_type_attr(
        _type, "required_food_energy", 13000.0, units=food_energy_units,
        description="Required food energy content")
    data["human_max_starvation_days"] = create_agent_type_attr(
        _type, "max_starvation_days", 21.0, units="days",
        description="Max time a human can go without food.")

    # max energy a human can have
    data["human_max_energy"] = create_agent_type_attr(
        _type, "max_energy", 21.0 * 13000.0, units=food_energy_units,
        description="Number of days a person can go with "
            "food times metabolic rate in kJ")

    # water usage
    data["human_max_dehydration_days"] = create_agent_type_attr(
        _type, "max_dehydration_days", 3.0, units="days",
        description="Max time a human can go without water.")
    data["human_consumed_water_usage"] = create_agent_type_attr(
        _type, "consumed_water_usage", 2.5, units=mass_usage_units,
        description="Water consumed by the human.")
    data["human_hygiene_water_usage"] = create_agent_type_attr(
        _type, "hygiene_water_usage", 7.17, units=mass_usage_units,
        description="Water consumed for hygiene, urinal, shower.")
    data["human_medical_water_usage"]  = create_agent_type_attr(
        _type, "medical_water_usage", 0.5, units=mass_usage_units,
        description="Water consumed for medical purposes")

    # water output
    # TODO sort out discrepency between water usage
    # and water output
    data["human_grey_water_output"] = create_agent_type_attr(_type,
        "grey_water_output", 1.584, units=mass_usage_units,
        description="Water converted to grey water by a human per day not including solid content.")
    data["human_waste_water_output"] = create_agent_type_attr(_type,
        "waste_water_output", 8.6, units=mass_usage_units,
        description="Water converted to waste water by a human per day.")
    data["human_solid_waste_water_output"] = create_agent_type_attr(_type,
        "solid_waste_water_output", .02, units=mass_usage_units,
        description="Water content in solid waste output of a human per day.")

    # respiration
    data["human_oxygen_consumption"] = create_agent_type_attr(_type,
        "oxygen_consumption", 0.818, units=mass_usage_units,
        description="Oxygen consumed by a human per day.")
    data["human_carbon_produced"] = create_agent_type_attr(_type,
        "carbon_produced", 1.037, units=mass_usage_units,
        description="Carbon dioxide produced by a human per day.")
    # solid waste
    data["human_grey_water_solid_output"] = create_agent_type_attr(_type,
        "grey_water_solid_output", 1.503, units=mass_usage_units,
        description="Solid content of grey water output by a human per day.")
    data["human_solid_waste_output"] = create_agent_type_attr(_type,
        "solid_waste_output", .1, units=mass_usage_units,
        description="Solid waste output of a human per day, not including water content.")

    # fatal gas levels
    data["human_fatal_o2"] = create_agent_type_attr(
        _type, "fatal_o2_lower", 15.7, units=gas_units,
        description="Fatal lower limit of O2")
    data["human_fatal_co2"] = create_agent_type_attr(
        _type, "fatal_co2_upper", 0.53, units=gas_units,
        description="Fatal upper limit of O2")

    data["human_work_day_hours"] = create_agent_type_attr(
        _type, "work_day_hours", 10, units="hours",
        description="Work hours in a day.")
    # Metabolism function values
    metabolic_description_format = \
        "{} in metabolic function: work_factor * time(days) * (A - (age_factor*age(years)) + B(mass_factor*mass(kg) + height_factor*height(m)))/C"

    data["human_metabolism_A"] = create_agent_type_attr(
        _type, "metabolism_A", 622.0, units=UNITLESS,
        description=metabolic_description_format.format("A"))
    data["human_metabolism_age_factor"] = create_agent_type_attr(
        _type, "metabolism_age_factor", 9.53, units=UNITLESS,
        description=metabolic_description_format.format("age_factor"))
    data["human_metabolism_B"] = create_agent_type_attr(
        _type, "metabolism_B", 1.25, units=UNITLESS,
        description=metabolic_description_format.format("B"))
    data["human_metabolism_mass_factor"] = create_agent_type_attr(
        _type, "metabolism_mass_factor", 15.9, units=UNITLESS,
        description=metabolic_description_format.format("mass_factor"))
    data["human_metabolism_height_factor"] = create_agent_type_attr(
        _type, "metabolism_height_factor", 539.6, units=UNITLESS,
        description=metabolic_description_format.format("height_factor"))
    data["human_metabolism_C"] = create_agent_type_attr(
        _type, "metabolism_C", 0.238853e3, units=UNITLESS,
        description=metabolic_description_format.format("C"))
    data["human_metabolism_work_factor_idle"] = create_agent_type_attr(
        _type, "metabolism_work_factor_idle", 1, units=UNITLESS,
        description=metabolic_description_format.format("work_factor(while idle)"))
    data["human_metabolism_work_factor_working"] = create_agent_type_attr(
        _type, "metabolism_work_factor_working", 1.105, units=UNITLESS,
        description=metabolic_description_format.format("work_factor(while working)"))

    return data

def gen_plants():
    data = OrderedDict()
    #max_height estimates as well as any density with 250.00
                                      #oxygen, carbon, water, edible, inedible, growth period, density, max_height, energy density  fatal co2
    add_plant(data, "cabbage",       0.00719, 0.00988, 1.77,  0.07578,  0.00674,   85.0,       295.87,   0.508,      1170.0  )
    add_plant(data, "carrot",        0.01636, 0.02250, 1.77,  0.07483,  0.05987,   75.0,       541.02,   0.406,      1160.0  )
    add_plant(data, "chard",         0.01149, 0.01579, 1.77,  0.08750,  0.03769,   45.0,       152.16,   1.000,      980.0   )
    add_plant(data, "celery",        0.01224, 0.01683, 1.24,  0.10327,  0.01147,   75.0,       501.21,   0.762,      750.0   )
    add_plant(data, "dry_bean",      0.03067, 0.04217, 2.53,  0.01111,  0.15000,   85.0,       811.54,   0.965,      5740.0  )
    add_plant(data, "green_onion",   0.01067, 0.01467, 1.74,  0.08182,  0.01000,   50.0,       250.00,   0.508,      1333.0  )
    add_plant(data, "lettuce",       0.00778, 0.01070, 1.77,  0.13135,  0.00730,   28.0,       232.47,   1.219,      480.0   )
    add_plant(data, "pea",           0.01200, 0.01650, 1.74,  0.01220,  0.16100,   75.0,       250.00,   2.435,      4450.0  )
    add_plant(data, "peanut",        0.03584, 0.04928, 2.77,  0.00596,  0.16875,   104.0,      641.00,   1.219,      26040.0 )
    add_plant(data, "pepper",        0.02471, 0.03398, 1.77,  0.14894,  0.12743,   85.0,       506.00,   2.134,      1090.0  )
    add_plant(data, "radish",        0.01186, 0.01631, 1.77,  0.09167,  0.05500,   25.0,       250.00,   0.305,      760.0   )
    add_plant(data, "red_beet",      0.00711, 0.00977, 1.77,  0.03250,  0.03500,   38.0,       574.84,   0.914,      1430.0  )
    add_plant(data, "rice",          0.03655, 0.05026, 3.43,  0.01030,  0.21158,   85.0,       250.00,   1.524,      4030.0  )
    add_plant(data, "snap_bean",     0.03643, 0.05009, 2.46,  0.14850,  0.17820,   85.0,       250.00,   1.524,      910.0   )
    add_plant(data, "soybean",       0.01391, 0.01913, 2.88,  0.00504,  0.06804,   97.0,       753.00,   1.600,      17890.0 )
    add_plant(data, "spinach",       0.00778, 0.01070, 1.77,  0.07297,  0.00730,   30.0,       126.80,   0.610,      710.0   )
    add_plant(data, "strawberry",    0.02532, 0.03482, 2.22,  0.07788,  0.14446,   85.0,       642.47,   0.610,      1540.0  )
    add_plant(data, "sweet_potato",  0.04112, 0.05654, 2.88,  0.05172,  0.22500,   85.0,       634.01,   0.584,      4020.0  )
    add_plant(data, "tomato",        0.02636, 0.03624, 2.77,  0.17376,  0.12743,   85.0,       760.82,   2.134,      810.0   )
    add_plant(data, "wheat",         0.05600, 0.07700, 11.79, 0.02273,  0.30000,   79.0,       250.00,   1.321,      14460.0 )
    add_plant(data, "white_potato",  0.03223, 0.04523, 2.88,  0.10530,  0.09025,   132.0,      634.01,   1.372,      3570.0  )
    add_plant(data, "default_plant", 0.03000, 0.04000, 5.0,   0.05000,  0.05000,   85.0,       450.00,   1.000,      4444.0  ,      .015)

    return data


def add_plant(data, name, oxygen, carbon, water, edible,
        inedible, growth_period, density, max_height, energy_density,
        fatal_co2_lower=None):
    agent_type = AgentType(name=name)
    data["{0}_plant_agent_type".format(name)] = agent_type

    # TODO convert gas exchange values to kg
    create_agent_type_attr(agent_type, "oxygen_produced", oxygen, "kg/(m^2*day)",
        "Oxygen produced by the plant.")
    create_agent_type_attr(agent_type, "carbon_uptake", carbon, "kg/(m^2*day)",
        "Carbon uptake by the plant.")
    create_agent_type_attr(agent_type, "water_uptake", water, "kg/(m^2*day)",
        "Water uptake by the plant.")
    create_agent_type_attr(agent_type, "edible", edible, "(kg[dry weight]/(m^2*day)",
        "The edible mass created by the plant per day.")
    create_agent_type_attr(agent_type, "inedible", inedible, "(kg[dry weight]/(m^2*day)",
        "The inedible mass created by the plant per day.")
    create_agent_type_attr(agent_type, "growth_period", growth_period, units="days [after planted]", 
        description="Days until plant reaches maturity after planting.")
    create_agent_type_attr(agent_type, "density", density, units="kg/m^3", 
        description="Density of the plant matter")
    create_agent_type_attr(agent_type, "energy_density", energy_density, units="kJ/kg",
        description="Energy of the plant as a food in kilojoules per kilogram.")
    create_agent_type_attr(agent_type, "max_height", max_height, units="m", 
        description="The total height of the plant agent including root length")

    if fatal_co2_lower is not None:
        create_agent_type_attr(agent_type, "fatal_co2_lower", fatal_co2_lower, units="kPa",
            description="Lower limit on fatal co2 values.")

def gen_structures():
    data = OrderedDict()

    # set up default structure values
    data["default_structure_agent_type"] = AgentType(name="default_structure")

    add_structure(data, "airlock",          10, 10, 10, 50, 0.9, 10, 10)
    add_structure(data, "crew_quarters",    10, 10, 10, 50, 0.9, 10, 10)
    add_structure(data, "greenhouse",       10, 10, 10, 50, 0.9, 10, 10)
    add_structure(data, "kitchen",          10, 10, 10, 50, 0.9, 10, 10)
    add_structure(data, "power_station",    10, 10, 10, 50, 0.9, 10, 0)
    add_structure(data, "rocket_pad",       10, 10, 10, 50, 0.9, 10, 10)
    add_structure(data, "rover_dock",       10, 10, 10, 50, 0.9, 10, 0)
    add_structure(data, "storage_facility", 10, 10, 10, 50, 0.9, 10, 0)
    add_structure(data, "harvester",        10, 10, 10, 50, 0.9, 10, 0)
    add_structure(data, "planter",          10, 10, 10, 50, 0.9, 10, 0)

    # greenhouse specific values
    create_agent_type_attr(data["greenhouse_structure_agent_type"], "max_plants", 50)

    return data



def add_structure(data, name, length, width, height, mass, efficiency, 
        build_time, power_consumed):
    agent_type = AgentType(name=name)
    data["{0}_structure_agent_type".format(name)] = agent_type

    create_agent_type_attr(agent_type, "length", length, "m", "The length of the structure.")
    create_agent_type_attr(agent_type, "width", width, "m", "The width of the structure.")
    create_agent_type_attr(agent_type, "height", height, "m", "The height of the structure.")
    create_agent_type_attr(agent_type, "mass", mass, "kg", "The mass of the structure.")
    create_agent_type_attr(agent_type, "efficiency", efficiency, "", "The efficiency (if applicable) of the structure.")
    create_agent_type_attr(agent_type, "build_time", build_time, "hours", "Time to build the structure.")
    create_agent_type_attr(agent_type, "power_consumption", power_consumed, "kW/day", "How much power is consumed by the structure.")

    return agent_type

def create_agent_type_attr(agent_type, name, value, units=None, description=None):
    return AgentTypeAttribute(name=name, agent_type=agent_type, value=str(value),
        value_type=str(type(value).__name__), units=units, description=description)
