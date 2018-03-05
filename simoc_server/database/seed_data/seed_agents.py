from . import util
from collections import OrderedDict
from simoc_server.database.db_model import AgentType, AgentTypeAttribute


UNKNOWN_UNITS = "unknown"

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
    return data

def gen_human():
    data = OrderedDict()
    data["human_agent_type"] = AgentType(name="human")

    _type = data["human_agent_type"]

    age_units = "years"
    water_usage_units = "Kg/CrewMember*d"
    gas_units = "kPa"


    # specifies age limits for earth-to-colony humans
    data["human_min_arrival_age"] = create_agent_type_attr(
        _type, "min_arrival_age", 21.0, units=age_units,
        description="Minimum expected arrival age of a human coming"
            "from earth")
    data["human_max_arrival_age"] = create_agent_type_attr(
        _type, "max_arrival_age", 50.0, units=age_units,
        description="Maximum expected arrival age of a human coming"
            "from earth")

    # max energy a human can have
    data["human_max_energy"] = create_agent_type_attr(
        _type, "max_energy", 21.0 * 13, units="MJ",
        description="Number of days a person can go with "
            "food times metabolic rate in MJ")

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

    # water usage
    data["human_consumed_water_usage"] = create_agent_type_attr(
        _type, "consumed_water_usage", 2.5, units=water_usage_units,
        description="Water consumed by the human.")
    data["human_hygiene_water_usage"] = create_agent_type_attr(
        _type, "hygiene_water_usage", 7.17, units=water_usage_units,
        description="Water consumed for hygiene, urinal, shower.")
    data["human_medical_water_usage"]  = create_agent_type_attr(
        _type, "medical_water_usage", 0.5, units=water_usage_units,
        description="Water consumed for medical purposes")

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
        "{} in metabolic function: (A - (age_factor*age(years)) + B(mass_factor*mass(kg) + height_factor*height(m)))/(C * work_factor * time(days))"
        
    data["human_mmetabolism_A"] = create_agent_type_attr(
        _type, "metabolism_A", 622.0, units=UNKNOWN_UNITS,
        description=metabolic_description_format.format("A"))
    data["human_metabolism_age_factor"] = create_agent_type_attr(
        _type, "metabolism_age_factor", 9.53, units=UNKNOWN_UNITS,
        description=metabolic_description_format.format("age_factor"))
    data["human_metabolism_B"] = create_agent_type_attr(
        _type, "metabolism_B", 1.25, units=UNKNOWN_UNITS,
        description=metabolic_description_format.format("B"))
    data["human_metabolism_mass_factor"] = create_agent_type_attr(
        _type, "metabolism_mass_factor", 15.9, units=UNKNOWN_UNITS,
        description=metabolic_description_format.format("mass_factor"))
    data["human_metabolism_height_factor"] = create_agent_type_attr(
        _type, "metabolism_height_factor", 539.6, units=UNKNOWN_UNITS,
        description=metabolic_description_format.format("height_factor"))
    data["human_metabolism_C"] = create_agent_type_attr(
        _type, "metabolism_C", 0.238853e3, units=UNKNOWN_UNITS,
        description=metabolic_description_format.format("C"))
    data["human_metabolism_work_factor_idle"] = create_agent_type_attr(
        _type, "metabolism_work_factor_idle", 1, units=UNKNOWN_UNITS,
        description=metabolic_description_format.format("work_factor(while idle)"))
    data["human_metabolism_work_factor_working"] = create_agent_type_attr(
        _type, "metabolism_work_factor_working", 1.105, units=UNKNOWN_UNITS,
        description=metabolic_description_format.format("work_factor(while working)"))

    return data

def gen_plants():
    data = OrderedDict()
                                      #oxygen, carbon, water, edible, inedible
    add_plant(data, "cabbage",          7.19,    9.88, 1.77,  75.78,  6.74)
    add_plant(data, "carrot",           16.36,  22.50, 1.77,  74.83,  59.87)
    add_plant(data, "chard",            11.49,  15.79, 1.77,  87.50,  37.69)
    add_plant(data, "celery",           12.24,  16.83, 1.24,  103.27, 11.47)
    add_plant(data, "dry_bean",         30.67,  42.17, 2.53,  11.11,  150.00)
    add_plant(data, "green_onion",      10.67,  14.67, 1.74,  81.82,  10.00)
    add_plant(data, "lettuce",          7.78,   10.70, 1.77,  131.35, 7.30)
    add_plant(data, "pea",              12,     16.50, 1.74,  12.20,  161.00)
    add_plant(data, "peanut",           35.84,  49.28, 2.77,  5.96,   168.75)
    add_plant(data, "pepper",           24.71,  33.98, 1.77,  148.94, 127.43)
    add_plant(data, "radish",           11.86,  16.31, 1.77,  91.67,  55.00)
    add_plant(data, "red_beet",         7.11,   9.77,  1.77,  32.50,  35.00)
    add_plant(data, "rice",             36.55,  50.26, 3.43,  10.30,  211.58)
    add_plant(data, "snap_bean",        36.43,  50.09, 2.46,  148.50, 178.20)
    add_plant(data, "soybean",          13.91,  19.13, 2.88,  5.04,   68.04)
    add_plant(data, "spinach",          7.78,   10.70, 1.77,  72.97,  7.30)
    add_plant(data, "strawberry",       25.32,  34.82, 2.22,  77.88,  144.46)
    add_plant(data, "sweet_potato",     41.12,  56.54, 2.88,  51.72,  225.00)
    add_plant(data, "tomato",           26.36,  36.24, 2.77,  173.76, 127.43)
    add_plant(data, "wheat",            56,     77,    11.79, 22.73,  300.00)
    add_plant(data, "white_potato",     32.23,  45.23, 2.88,  105.30, 90.25)
    add_plant(data, "default_plant",    30,     40,    5,     50,     50)

    return data


def add_plant(data, name, oxygen, carbon, water, edible, inedible):
    agent_type = AgentType(name=name)
    data["{0}_plant_agent_type".format(name)] = agent_type

    create_agent_type_attr(agent_type, "oxygen_consumption", oxygen, "g/(m^2*day)",
        "Oxygen consumed by the plant.")
    create_agent_type_attr(agent_type, "carbon_uptake", carbon, "g/(m^2*day)",
        "Carbon uptake by the plant.")
    create_agent_type_attr(agent_type, "water_uptake", water, "kg/(m^2*day)",
        "Water uptake by the plant.")
    create_agent_type_attr(agent_type, "edible", edible, "(g[dry weight]/(m^2*day)",
        "The edible mass created by the plant per day.")
    create_agent_type_attr(agent_type, "inedible", inedible, "(g[dry weight]/(m^2*day)",
        "The inedible mass created by the plant per day.")

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
    
    return data



def add_structure(data, name, length, width, height, mass, efficiency, 
        build_time, power_consumed,):
    agent_type = AgentType(name=name)
    data["{0}_structure_agent_type".format(name)] = agent_type

    create_agent_type_attr(agent_type, "length", length, "m", "The length of the structure.")
    create_agent_type_attr(agent_type, "width", width, "m", "The width of the structure.")
    create_agent_type_attr(agent_type, "height", height, "m", "The height of the structure.")
    create_agent_type_attr(agent_type, "mass", mass, "kg", "The mass of the structure.")
    create_agent_type_attr(agent_type, "efficiency", efficiency, "", "The efficiency (if applicable) of the structure.")
    create_agent_type_attr(agent_type, "build_time", build_time, "hours", "Time to build the structure.")
    create_agent_type_attr(agent_type, "power_consumption", power_consumed, "kW/day", "How much power is consumed by the structure.")


def create_agent_type_attr(agent_type, name, value, units=None, description=None):
    return AgentTypeAttribute(name=name, agent_type=agent_type, value=str(value),
        value_type=str(type(value).__name__), units=units, description=description)
