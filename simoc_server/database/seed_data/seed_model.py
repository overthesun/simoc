from . import util
from collections import OrderedDict
from simoc_server.database.db_model import AgentModelParam



def seed():
    params = gen_params()

    util.add_all(params)

def gen_params():
    def create_param(name, value, description):
        return AgentModelParam(name=name, value=str(value),
            value_type=str(type(value).__name__))

    data = OrderedDict()

    data["minutes_per_step"] = create_param(name="minutes_per_step", \
            value=60, description="Number of minutes per 1 model step.")

    return data