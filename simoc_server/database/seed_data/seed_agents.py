from . import util
from collections import OrderedDict
from simoc_server.database.db_model import AgentType, AgentTypeAttribute


def seed():
    human_data = gen_human()
    plant_data = gen_plants()

    util.add_all(human_data)
    util.add_all(plant_data)



def gen_human():
    data = OrderedDict()
    data["human_agent_type"] = AgentType(name="human")

    # max energy a human can have
    data["human_max_energy_attr"] = create_agent_type_attr(
        data["human_agent_type"], "max_energy", 100)


    return data

def gen_plants():
    data = OrderedDict()

    add_plant(data, "cabbage", 7.19, 9.88, 1.77, 75.78, 6.74)
    add_plant(data, "carrot", 16.36, 22.50, 1.77, 74.83, 59.87)
    add_plant(data, "chard", 11.49, 15.79, 1.77, 87.50, 37.69)
    add_plant(data, "celery", 12.24, 16.83, 1.24, 103.27, 11.47)
    add_plant(data, "cry_bean", 30.67, 42.17, 2.53, 11.11, 150.00)
    add_plant(data, "green_onion", 10.67, 14.67, 1.74, 81.82, 10.00)
    add_plant(data, "lettuce", 7.78, 10.70, 1.77, 131.35, 7.30)
    add_plant(data, "pea", 12, 16.50, 1.74, 12.20, 161.00)
    add_plant(data, "peanut", 35.84, 49.28, 2.77, 5.96, 168.75)
    add_plant(data, "pepper", 24.71, 33.98, 1.77, 148.94, 127.43)
    add_plant(data, "radish", 11.86, 16.31, 1.77, 91.67, 55.00)
    add_plant(data, "red_beet", 7.11, 9.77, 1.77, 32.50, 35.00)
    add_plant(data, "rice", 36.55, 50.26, 3.43, 10.30, 211.58)
    add_plant(data, "snap_bean", 36.43, 50.09, 2.46, 148.50, 178.20)
    add_plant(data, "soybean", 13.91, 19.13, 2.88, 5.04, 68.04)
    add_plant(data, "spinach", 7.78, 10.70, 1.77, 72.97, 7.30)
    add_plant(data, "strawberry", 25.32, 34.82, 2.22, 77.88, 144.46)
    add_plant(data, "sweet_potato", 41.12, 56.54, 2.88, 51.72, 225.00)
    add_plant(data, "tomato", 26.36, 36.24, 2.77, 173.76, 127.43)
    add_plant(data, "wheat", 56, 77, 11.79, 22.73, 300.00)
    add_plant(data, "white_potato", 32.23, 45.23, 2.88, 105.30, 90.25)
    add_plant(data, "default_plant", 30, 40, 5, 50, 50)

    return data


def add_plant(data, name, oxygen, carbon, water, edible, inedible):
    agent_type = AgentType(name=name)
    data["{0}_plant_agent_type"] = agent_type

    def add_plant_attribute(attribute_name, value, units):
        key = "{0}_{1}_attr".format(name, attribute_name)
        data[key] = create_agent_type_attr(agent_type, attribute_name, value, units)

    add_plant_attribute("oxygen_consumption", oxygen, "(g/m^2)*day")
    add_plant_attribute("carbon_uptake", carbon, "(g/m^2)*day")
    add_plant_attribute("water_uptake", water, "(kg/m^2)*day")
    add_plant_attribute("edible", edible, "(g[dry weight]/m^2)*day")
    add_plant_attribute("inedible", inedible, "(g[dry weight]/m^2)*day")


def create_agent_type_attr(agent_type, name, value, units=None):
    return AgentTypeAttribute(name=name, agent_type=agent_type, value=str(value),
        value_type=str(type(value).__name__), units=units)