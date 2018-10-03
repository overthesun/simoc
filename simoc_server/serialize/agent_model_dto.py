from . import BaseDTO, AgentDTO

class AgentModelDTO(BaseDTO):

    AGENT_MODEL_ATTRIBUTES = [
        # "step_num",
        # "avg_oxygen_pressure",
        # "avg_carbon_dioxide_pressure",
        # "avg_nitrogen_pressure",
        # "avg_argon_pressure",
        # "total_water",
        # "total_waste_water",
        # "total_grey_water",
        # "total_grey_water_solids",
        # "total_solid_waste",
        # "total_food_energy",
        # "total_food_mass",
        # "total_humans",
        # "hours_per_step",
        # "total_biomass",
        # "total_inedible_biomass",
        # "total_electric_energy_capacity",
        # "total_electric_energy_capacity",
        # "total_electric_energy_usage",
        # "max_electric_output_capacity",
        # "total_electric_energy_charge",
        # "total_power_production",
        # "total_power_draw",
    ]

    def __init__(self, agent_model):
        self.agent_model = agent_model

    def get_state(self):
        state = {}

        for model_attr in self.AGENT_MODEL_ATTRIBUTES:
            state[model_attr] = getattr(self.agent_model, model_attr)

        agents = []
        for agent in self.agent_model.scheduler.agents:
            agents.append(AgentDTO(agent).get_state())
        state["agents"] = agents
        state["alerts"] = self.agent_model.active_alerts

        return state

    def get_state_diff(self, prev_state):
        # TODO implement
        pass