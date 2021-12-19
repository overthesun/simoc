def get_variable(gen, upper, lower, distribution):
    if distribution == 'normal':
        # TODO: Use skewed normal distribution instead
        max = 1 + upper
        min = 1 - lower
        mean = (max+min)/2      # Shift mean to center of min/max
        stdev = (max-mean)/3    # Upper/lower encompases 99.7% of cases
        return gen.normal(mean, stdev)
    elif distribution == 'exponential':
        if upper > 0:
            delta = gen.exponential(upper/3)
            return 1 + delta
        elif lower > 0:
            delta = gen.exponential(lower/3)
            return 1 - delta
        else:
            return 1
    elif distribution == 'uniform':
        return gen.uniform(1-lower, 1+upper)
