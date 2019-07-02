r"""Describes Core Agent Types.
"""
import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler
import functools
from scipy.optimize import minimize
from scipy.optimize import Bounds

np.seterr(over='ignore')


def get_bell_curve(num_values, min_value, max_value, scale, center=None, invert=False,
                   noise=False, noise_factor=10.0, clip=False, **kwargs):
    """TODO

    TODO

    Args:
      num_values: int, TODO
      min_value: float, TODO
      max_value: float, TODO
      center: float, TODO
      scale: float, TODO
      invert: bool, TODO
      noise: bool, TODO
      noise_factor: float, TODO
      clip: bool, TODO
      kwargs: Dict, unused arguments.

    Returns:
      TODO
    """
    del kwargs
    assert num_values
    assert min_value is not None
    assert max_value is not None
    assert scale is not None
    center = center or num_values / 2
    x = np.linspace(0, num_values, num_values)
    y = norm.pdf(x, center, scale)
    y = MinMaxScaler((min_value, max_value)).fit_transform(y.reshape(-1, 1))
    y = y.reshape(num_values)
    if invert:
        y = -1 * y
        y = y + max_value + min_value
    if noise:
        noise = np.random.normal(0, y.std() / noise_factor, num_values)
        y += noise
    if clip:
        y = np.clip(y, min_value, max_value)
    return y


def optimize_bell_curve_mean(mean_value, num_values, center, min_value, invert,
                             noise, noise_factor=10, **kwargs):
    del kwargs
    _get_bell_curve = functools.partial(get_bell_curve, num_values=num_values, center=center,
                                        min_value=min_value, invert=invert, noise=noise,
                                        noise_factor=noise_factor)

    def _loss(args):
        scale, max_value = args[0], args[1]
        y = _get_bell_curve(scale=scale, max_value=max_value)
        rmse = np.sqrt(
            (np.abs(mean_value - np.mean(y)) +
             np.abs(y[0] - min_value)
             + np.abs(y[-1] - min_value)) ** 2)
        return rmse

    x0 = np.array([num_values / 2, mean_value])
    res = minimize(_loss, x0, bounds=Bounds([1e-10, min_value+1e-10], [1e10, 1e10]), options={'disp': False})
    return {'scale': res.x[0], 'max_value': res.x[1]}


def get_sigmoid_curve(num_values, min_value, max_value, steepness, center=None, noise=False,
                      noise_factor=10.0, clip=False, **kwargs):
    """TODO

    TODO

    Args:
      num_values: int, TODO
      min_value: float, TODO
      max_value: float, TODO
      center: float, TODO
      steepness: float, TODO
      noise: bool, TODO
      noise_factor: float, TODO
      clip: bool, TODO
      kwargs: Dict, unused arguments.

    Returns:
      TODO
    """
    del kwargs
    assert num_values
    assert min_value is not None
    assert max_value is not None
    assert steepness is not None
    center = center or num_values // 2
    x = np.linspace(0, num_values, num_values)
    y = ((max_value - min_value) / (1. + np.exp(-steepness * (x - center)))) + min_value
    y = MinMaxScaler((min_value, max_value)).fit_transform(y.reshape(-1, 1))
    y = y.reshape(num_values)
    if noise:
        noise = np.random.normal(0, y.std() / noise_factor, num_values)
        y += noise
    if clip:
        y = np.clip(y, min_value, max_value)
    return y


def optimize_sigmoid_curve_mean(mean_value, num_values, center, min_value,
                                noise, noise_factor=10.0, **kwargs):
    del kwargs
    _get_sigmoid_curve = functools.partial(get_sigmoid_curve, num_values=num_values, center=center,
                                           min_value=min_value, noise=noise,
                                           noise_factor=noise_factor)

    def _loss(args):
        steepness, max_value = args
        y = _get_sigmoid_curve(steepness=steepness, max_value=max_value)
        rmse = np.sqrt(np.abs(mean_value - np.mean(y)) ** 2)
        return (rmse / mean_value) + (steepness / num_values)

    x0 = np.array([num_values / 2, mean_value])
    res = minimize(_loss, x0, bounds=Bounds([1e-2, 1e-10], [num_values / 2, 1e10]), options={'disp': False})
    return {'steepness': res.x[0], 'max_value': res.x[1]}


def get_log_curve(num_values, max_value, min_value, zero_value=1e-2, noise=False,
                  noise_factor=10.0, clip=False, **kwargs):
    """TODO

    TODO

    Args:
      max_value: float, TODO
      num_values: int, TODO
      min_value: float, TODO
      zero_value: float, TODO
      noise: bool, TODO
      noise_factor: float, TODO
      clip: bool, TODO
      kwargs: Dict, unused arguments.

    Returns:
      TODO
    """
    del kwargs
    assert num_values
    assert min_value is not None
    assert max_value is not None
    zero_value = zero_value if zero_value < max_value else max_value * zero_value
    y = np.geomspace(zero_value, max_value - min_value, num_values) + min_value
    if noise:
        noise = np.random.normal(0, y.std() / noise_factor, num_values)
        y += noise
    if clip:
        y = np.clip(y, min_value, max_value)
    return y


def get_linear_curve(num_values, max_value, min_value, noise=False, noise_factor=10.0,
                     clip=False, **kwargs):
    """TODO

    TODO

    Args:
      max_value: float, TODO
      num_values: int, TODO
      min_value: float, TODO
      noise: bool, TODO
      noise_factor: float, TODO
      clip: bool, TODO
      kwargs: Dict, unused arguments.

    Returns:
      TODO
    """
    del kwargs
    assert num_values
    assert min_value is not None
    assert max_value is not None
    y = np.linspace(min_value, max_value, num_values)
    if noise:
        noise = np.random.normal(0, y.std() / noise_factor, num_values)
        y += noise
    if clip:
        y = np.clip(y, min_value, max_value)
    return y


def get_switch_curve(num_values, min_value, max_value, min_threshold, max_threshold,
                     noise=False, noise_factor=10.0, clip=False, **kwargs):
    """TODO

    TODO

    Args:
      max_value: float, TODO
      min_threshold: float, TODO
      max_threshold: float, TODO
      num_values: int, TODO
      min_value: float, TODO
      noise: bool, TODO
      noise_factor: float, TODO
      clip: bool, TODO
      kwargs: Dict, unused arguments.

    Returns:
      TODO
    """
    del kwargs
    assert num_values
    assert min_value is not None
    assert max_value is not None
    assert min_threshold is not None
    assert max_threshold is not None
    y = np.zeros(num_values) + min_value
    y[min_threshold:max_threshold] = max_value
    if noise:
        noise = np.random.normal(0, y.std() / noise_factor,
                                 min(max_threshold, y.shape[0]) - min_threshold)
        y[min_threshold:max_threshold] += noise
    if clip:
        y = np.clip(y, min_value, max_value)
    return y


def get_growth_values(agent_value, growth_type, **kwargs):
    """TODO

    TODO

    Args:
      agent_value: float, TODO
      growth_type: str, TODO
      kwargs: Dict, TODO

    Returns:
      TODO
    """
    assert growth_type
    assert agent_value is not None
    if growth_type in ['linear', 'lin']:
        return get_linear_curve(max_value=agent_value, **kwargs)
    elif growth_type in ['logarithmic', 'log']:
        return get_log_curve(max_value=agent_value, **kwargs)
    elif growth_type in ['sigmoid', 'sig']:
        return get_sigmoid_curve(max_value=agent_value, **kwargs)
    elif growth_type in ['norm', 'normal']:
        return get_bell_curve(max_value=agent_value, **kwargs)
    elif growth_type in ['step', 'switch']:
        return get_switch_curve(max_value=agent_value, **kwargs)
    else:
        raise ValueError("Unknown growth function type '{}'.".format(growth_type))