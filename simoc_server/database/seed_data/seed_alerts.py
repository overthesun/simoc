from . import util
from collections import OrderedDict
from simoc_server.database.db_model import Alert, AlertAttribute



def seed():
    low_o2_alert = gen_low_o2_alert()
    high_co2_alert = gen_high_co2_alert()
    human_death_alert = gen_human_death_alert()
    no_water_alert = gen_no_water_alert()
    no_food_alert = gen_no_food_alert()
    battery_charge_alert = gen_battery_charge_alert()

    util.add_all(low_o2_alert)
    util.add_all(high_co2_alert)
    util.add_all(human_death_alert)
    util.add_all(no_water_alert)
    util.add_all(no_food_alert)
    util.add_all(battery_charge_alert)

def gen_low_o2_alert():
    data = OrderedDict()

    data["low_o2_alert"] = alert = Alert(name="low_o2_alert")
    # TODO determine realistic value for low o2 alert
    data["low_o2_thresh"] = create_alert_attr(alert, "low_o2_thresh", 
        17.0, "kPa", description="Lower bound for O2 levels to trigger"
            " low oxygen alert.")
    return data

def gen_high_co2_alert():
    data = OrderedDict()

    data["high_co2_alert"] = alert = Alert(name="high_co2_alert")
    data["high_co2_thresh"] = create_alert_attr(alert, "high_co2_thresh", 
        .10, "kPa", description="Upper bound for CO2 levels to trigger"
        " high co2 alert.")

    return data

def gen_human_death_alert():
    data = OrderedDict()

    data["human_death_alert"] = alert = Alert(name="human_death_alert")
    return data

def gen_no_water_alert():
    data = OrderedDict()

    data["no_water_alert"] = alert = Alert(name="no_water_alert")
    return data

def gen_no_food_alert():
    data = OrderedDict()
    
    data["no_food_alert"] = alert = Alert(name="no_food_alert")
    return data

def gen_battery_charge_alert():
    data = OrderedDict()
    
    data["battery_charge_alert"] = alert = Alert(name="battery_charge_alert")
    return data

def create_alert_attr(alert, name, value, units=None, description=None):
    return AlertAttribute(name=name, alert=alert, value=str(value),
        value_type=str(type(value).__name__), units=units, description=description)