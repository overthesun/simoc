import statistics

import pytest
from pytest import approx

from agent_model.agents.variation_func import get_variable

def mean(array):
    return sum(array) / len(array)

def stdev(array):
    return statistics.stdev(array)

def test_normal(random_state):
    upper = 0.2
    lower = 0.2
    distribution = 'normal'
    samples = []
    for i in range(10):
        samples.append(get_variable(random_state, upper, lower, distribution))
    assert samples[0] == 0.9931764113505096
    assert stdev(samples) == 0.028197265385736036

def test_normal_stdev(random_state):
    upper = 0.2
    lower = 0.2
    distribution = 'normal'
    stdev_range = 3
    samples = []
    for i in range(10):
        samples.append(get_variable(random_state, upper, lower, distribution, stdev_range))
    assert samples[0] == 0.9863528227010191
    assert stdev(samples) == 0.05639453077147215

def test_exponential_positive(random_state):
    upper = 0.5
    lower = 0
    distribution = 'exponential'
    samples = []
    for i in range(10):
        samples.append(get_variable(random_state, upper, lower, distribution))
    assert samples[0] == 1.4422984388502913
    assert mean(samples) == 1.200828725595863

def test_exponential_negative(random_state):
    upper = 0
    lower = 0.5
    distribution = 'exponential'
    samples = []
    for i in range(10):
        samples.append(get_variable(random_state, upper, lower, distribution))
    assert samples[0] == 0.5577015611497086
    assert mean(samples) == 0.7991712744041369
