from operator import invert
from agent_model.agents.growth_func import *
from pytest import approx


def test_optimize_bell_curve_mean(agent_desc):
    # based on rice.out_biomass
    value = 0.001259583
    lifetime = 2040
    result = optimize_bell_curve_mean(mean_value=value,
                                      num_values=lifetime,
                                      center=lifetime/2,
                                      min_value=0,
                                      invert=False,
                                      noise=False)
    assert result['max_value'] == 0.005027526800753942

def test_get_bell_curve():
    # based on rice.out_biomass
    value = 0.001259583
    lifetime=2040
    max_value = 0.005027526800753942  # from optimize_bell_curve
    result = get_bell_curve(num_values=lifetime,
                            min_value=0,
                            max_value=max_value,
                            scale=0.1,  # defaults..
                            center=None,
                            invert=False,
                            noise=False,
                            noise_factor=10.0,
                            clip=False)
    assert len(result) == lifetime
    assert sum(result) == approx(value * lifetime)

def test_optimize_sigmoid_curve_mean():
    # based on rice.in_potb
    value = 0.0079341666667
    lifetime = 2040
    result = optimize_sigmoid_curve_mean(mean_value=value,
                                         num_values=lifetime,
                                         center=int(lifetime/2),
                                         min_value=0,
                                         noise=False,
                                         noise_factor=10.0)
    assert result['steepness'] == approx(1020)
    assert result['max_value'] == 0.01587611172150995

def test_get_sigmoid_curve():
    # based on rice.in_potb
    value = 0.0079341666667
    lifetime = 2040
    max_value = 0.01587611172150995  # from optimize_sigmoid_curve_mean
    result = get_sigmoid_curve(num_values=lifetime,
                               min_value=0,
                               max_value=max_value,
                               steepness=1.0,  # defaults..
                               center=None,
                               noise=False,
                               noise_factor=10.0,
                               width=10,
                               clip=False)

    assert len(result) == lifetime
    assert sum(result) == approx(value * lifetime)
