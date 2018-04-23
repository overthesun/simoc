from abc import ABCMeta

from simoc_server import db
from simoc_server.util import load_db_attributes_into_dict
from simoc_server.database.db_model import AlertAttribute, Alert
from simoc_server.agent_model import agents

class AlertsWatcher(object):

    def __init__(self, model):
        self.model = model
        self.add_alerts()

    def add_alerts(self):
        self.alert_handlers = []
        self.alert_handlers.append(LowO2Alert(self.model))
        self.alert_handlers.append(HighCo2Alert(self.model))
        self.alert_handlers.append(HumanDeathAlert(self.model))
        self.alert_handlers.append(NoWaterAlert(self.model))
        self.alert_handlers.append(NoFoodAlert(self.model))
        self.alert_handlers.append(BatteryChargeAlert(self.model))

    def get_alerts(self):
        alerts = []
        for handler in self.alert_handlers:
            print("checking", handler)
            alerts += handler.get_alerts()
        return alerts

class BaseAlertHandler(object, metaclass=ABCMeta):

    """The BaseAlert class from which all alerts
    should be derived.
    
    Attributes
    ----------
    alert_attributes : dict
        A dict containing loaded attributes for the 
        class
    model : simoc_server.agent_model.AgentModel
        A reference to the agent model to monitor for
        alerts.
    """

    _alert_name = None

    def __init__(self, model):
        self.model = model
        self.load_attributes()

    def get_alerts(self):
        """A method to be overridden in subclasses. Should
        check for alerts and return a list containing any
        found (using new_alert)
        
        Raises
        ------
        NotImplementedError
            If called in a subclass that has not implemented this
            method.
        """
        raise NotImplementedError("Must override this method.")

    def load_attributes(self):
        """Loads the attributes for the class if they haven't already
        been loaded
        """
        if not hasattr(self.__class__, "alert_attributes"):
            alert = Alert.query.filter_by(name=self.__class__._alert_name).first()
            self.alert_attributes = load_db_attributes_into_dict(alert.alert_attributes)

    def get_alert_attribute(self, name):
        """Gets an attribute associated with this alert
        
        Parameters
        ----------
        name : type of attribute
            The name of the attribute to get
        
        Returns
        -------
        TYPE
            Returns the alert attribute with the given name
        """
        return self.__class__.alert_attributes[name]

    def new_alert(self, description):
        """Create a new alert
        
        Parameters
        ----------
        description : str
            A description of the alert
        
        Returns
        -------
        dict
            Dictionary containing the "name" and
            "description" of the alert
        """
        return {
            "name":self._alert_name,
            "description":description
        }

class LowO2Alert(BaseAlertHandler):
    _alert_name = "low_o2_alert"

    def get_alerts(self):
        """Check each atmosphere to see if any have lower o2
        levels than the value stored in "low_o2_thresh"
        
        Returns
        -------
        list
            A list containing an alert if any o2 levels are
            below the threshold
        """
        for atmosphere in self.model.atmospheres:
            if atmosphere.oxygen < self.alert_attributes["low_o2_thresh"]:
                alert = self.new_alert("Oxygen levels dangerously low: {0:.3f}"
                    .format(atmosphere.oxygen))
                return [alert]

        return []


class HighCo2Alert(BaseAlertHandler):
    _alert_name = "high_co2_alert"

    def get_alerts(self):
        """Check each atmosphere to see if any have higher co2
        levels than the value stored in "high_co2_thresh"
        
        Returns
        -------
        list
            A list containing an alert if any co2 levels are
            above the threshold
        """
        for atmosphere in self.model.atmospheres:
            if atmosphere.carbon_dioxide > self.alert_attributes["high_co2_thresh"]:
                alert = self.new_alert("CO2 levels dangerously high: {0:.3f}"
                    .format(atmosphere.carbon_dioxide))
                return [alert]

        return []


class HumanDeathAlert(BaseAlertHandler):
    _alert_name = "human_death_alert"

    def __init__(self, model):
        super().__init__(model)
        self.previous_humans = self.get_humans()

    def get_alerts(self):
        """Trigger an alert if any humans die.
        
        Returns
        -------
        list
            A list containing a single alert if
            any humans die, will indicate the amount.
        """
        current_humans = self.get_humans()

        diff = self.previous_humans - current_humans
        lost_humans = len(diff)
        alerts = []
        if lost_humans > 0:
            _s = "'s" if lost_humans > 1 else ""
            alert = self.new_alert("{} human{} lost.".
                format(lost_humans, _s))
            alerts.append(alert)
        previous_humans = current_humans
        return alerts


    def get_humans(self):
        return set(self.model.get_agents(agents.HumanAgent))

class NoWaterAlert(BaseAlertHandler):

    _alert_name = "no_water_alert"

    def get_alerts(self):
        if self.model.total_water == 0:
            return [self.new_alert("There is no water.")]
        return []

class NoFoodAlert(BaseAlertHandler):

    _alert_name = "no_food_alert"

    def get_alerts(self):
        if self.model.total_food_mass == 0:
            return [self.new_alert("There is no food.")]
        return []

class BatteryChargeAlert(BaseAlertHandler):

    _alert_name = "battery_charge_alert"

    def get_alerts(self):
        if self.model.total_power_charge == 0:
            return [self.new_alert("There is no power.")]
        return []