r"""Describes Core Agent Types.
"""
import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler
import functools
from scipy.optimize import minimize
from scipy.optimize import Bounds

np.seterr(over='ignore')


# Caching norm.pdf() directly is not possible since
# x0 is a non-hashable numpy.ndarray.  x0 depends
# on num_values, so we can create this helper function
# and cache num_values, scale, and center instead.
# This makes DB initializazion much faster, since
# of the 15k calls done, all except 12 can be cached.
# We also can't use lru_cache() directly because the
# return value is a mutable ndarray, and we need to
# explicitly create and return a copy.
def norm_pdf(num_values, scale, center, *, _cache={}):
    if (num_values, scale, center) in _cache:
        y = _cache[(num_values, scale, center)].copy()
    else:
        center = center or num_values // 2
        x0 = np.linspace(0, 1, num_values)
        y = norm.pdf(x0, x0[center], scale)
        _cache[(num_values, scale, center)] = y
    return y


def get_bell_curve(num_values, min_value, max_value, scale=0.1, center=None, invert=False,
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
    y = norm_pdf(num_values, scale, center)
    y = MinMaxScaler((min_value, max_value)).fit_transform(y.reshape(-1, 1)).reshape(num_values)
    if invert:
        y = -1 * y
        y = y + max_value + min_value
    if noise:
        noise = np.random.normal(0, y.std() / noise_factor, num_values)
        y += noise
    if clip:
        y = np.clip(y, min_value, max_value)
    return y


def get_clipped_bell_curve(num_values, min_value, max_value, scale=0.1, factor=2, center=None,
                           invert=False, noise=False, noise_factor=10.0, **kwargs):
    """TODO

    TODO

    Args:
      num_values: int, TODO
      min_value: float, TODO
      max_value: float, TODO
      center: float, TODO
      scale: float, TODO
      factor: float, TODO
      invert: bool, TODO
      noise: bool, TODO
      noise_factor: float, TODO
      kwargs: Dict, unused arguments.

    Returns:
      TODO
    """
    del kwargs
    assert num_values
    assert min_value is not None
    assert max_value is not None
    assert scale is not None
    y = norm_pdf(num_values, scale, center)
    y = MinMaxScaler((min_value, max_value * factor)).fit_transform(y.reshape(-1, 1)).reshape(num_values)
    y = np.clip(y, min_value, max_value)
    if invert:
        y = -1 * y
        y = y + max_value + min_value
    if noise:
        noise = np.random.normal(0, y.std() / noise_factor, num_values)
        y += noise
    return y


def optimize_bell_curve_mean(mean_value, num_values, center, min_value, invert,
                             noise, noise_factor=10, **kwargs):
    del kwargs
    _get_bell_curve = functools.partial(get_bell_curve, num_values=num_values, center=center,
                                        min_value=min_value, invert=invert, noise=noise,
                                        noise_factor=noise_factor)

    def _loss(max_value):
        y = _get_bell_curve(max_value=max_value)
        rmse = np.sqrt(
            (np.abs(mean_value - np.mean(y)) +
             np.abs(y[0] - min_value)
             + np.abs(y[-1] - min_value)) ** 2)
        return rmse

    res = minimize(_loss, mean_value, bounds=[[max(1e-8, mean_value), 1e8]], options={'disp': False})
    return {'max_value': res.x[0]}


# this function manually caches some calculations,
# similarly to the norm_pdf function above
def calc_y(num_values, width, center, steepness, *, _cache={}):
    if (num_values, width, center, steepness) in _cache:
        y = _cache[(num_values, width, center, steepness)].copy()
    else:
        center = center or num_values // 2
        x0 = np.linspace(-width, width, num_values)
        y = 1 / (1. + np.exp(-steepness * (x0 - x0[center])))
        _cache[(num_values, width, center, steepness)] = y
    return y

def get_sigmoid_curve(num_values, min_value, max_value, steepness=1.0, center=None, noise=False,
                      noise_factor=10.0, width=10, clip=False, **kwargs):
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
      width: int, TODO
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
    y = calc_y(num_values, width, center, steepness)
    y = MinMaxScaler((min_value, max_value)).fit_transform(y.reshape(-1, 1)).reshape(num_values)
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
    if kwargs.get('max_value', 0.0) <= 0:
        kwargs['max_value'] = agent_value
    if growth_type in ['linear', 'lin']:
        return get_linear_curve(**kwargs)
    elif growth_type in ['logarithmic', 'log']:
        return get_log_curve(**kwargs)
    elif growth_type in ['sigmoid', 'sig']:
        return get_sigmoid_curve(**kwargs)
    elif growth_type in ['norm', 'normal']:
        return get_bell_curve(**kwargs)
    elif growth_type in ['clipped', 'clip']:
        return get_clipped_bell_curve(**kwargs)
    elif growth_type in ['step', 'switch']:
        return get_switch_curve(**kwargs)
    else:
        raise ValueError("Unknown growth function type '{}'.".format(growth_type))
