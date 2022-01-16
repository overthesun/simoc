def get_variable(gen, upper, lower, distribution, stdev_range=None):
    if distribution == 'normal':
        # TODO: Use skewed normal distribution instead
        max = 1 + upper
        min = 1 - lower
        mean = (max+min)/2      # Shift mean to center of min/max
        if stdev_range:
            stdev = (max - mean)/stdev_range
        else:
            stdev = (max-mean)/6    # Upper/lower encompases 99.7% of cases
        return gen.normal(mean, stdev)
    elif distribution == 'exponential':
        if upper > 0:
            delta = gen.exponential(upper/3)
            return 1 + delta
        elif lower > 0:
            delta = gen.exponential(lower/3)
            return 1 - delta
