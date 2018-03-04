import datetime

def load_db_attributes_into_dict(attributes, target=None):
    if target is None:
        target = {}

    for attribute in attributes:
        # get type of attribute
        if attribute.value_type == type(None).__name__:
            value = None
        else:
            value_type = eval(attribute.value_type)
            value_str = attribute.value
            value = value_type(value_str)
        attribute_name = attribute.name
        target[attribute_name] = value

    return target


def extend_dict(dict_a, dict_b, in_place=False):
    return dict(dict_a, **dict_b)

def subdict_from_list(d, l):
    """Return a subset of d from a list of keys, l
    
    Parameters
    ----------
    d : dict
        Dictionary to take subset from
    l : list
        list of keys to make the subet
    
    Returns
    -------
    dict
        the subset of d defined by l
    """
    return {key:d[key] for key in l if key in d}


def timedelta_to_days(time_d):
    """Get total days from timedelta
    
    Parameters
    ----------
    time_d : datetime.timedelta
        the timedelta to get the days of
    
    Returns
    -------
    float
        total days represented by the timedelta object
    """
    return time_d / datetime.timedelta(days=1)

def timedelta_to_hours(time_d):
    """Get total days from timedelta
    
    Parameters
    ----------
    time_d : datetime.timedelta
        the timedelta to get the days of
    
    Returns
    -------
    float
        total days represented by the timedelta object
    """
    return time_d / datetime.timedelta(hours=1)

def timedelta_to_minutes(time_d):
    """Get total minutes from timedelta
    
    Parameters
    ----------
    time_d : datetime.timedelta
        the timedelta to get the minutes of
    
    Returns
    -------
    float
        total minutes represented by the timedelta object
    """
    return time_d / datetime.timedelta(minutes=1)

def timedelta_to_seconds(time_d):
    """Get total seconds from timedelta
    
    Parameters
    ----------
    time_d : datetime.timedelta
        the timedelta to get the seconds of
    
    Returns
    -------
    float
        total seconds represented by the timedelta object
    """
    return time_d.total_seconds()

def timedelta_hour_of_day(time_d):
    """Get the hour component of a timedelta object based on a
    24 hour day.

    This does not account for daylight savings time
    
    Parameters
    ----------
    time_d : datetime.timedelta
        the timedelta to get the hour of day from
    
    Returns
    -------
    float
        the hour of the day in the timedelta object
    """
    return time_d.seconds/float(datetime.timedelta(hours=1).total_seconds())



def sum_attributes(objects, attribute_name):
    """Sum all attributes in an iterable containing objects
    
    Parameters
    ----------
    objects : TYPE
        The objects containing attribute given
    attribute_name : TYPE
        the attribute to sum across the objects
    
    Returns
    -------
    type of object.attribute
        The sum of all of the attributes
    """
    return sum([x.__dict__[attribute_name] for x in objects])

def to_volume(mass, density):
    """ Converts the givin mass (in grams) and density (kg per cubic meter) to volume 

    Parameters
    ----------
    mass: grams
        The mass of the substance to be converted
    density: kg/m^3
        The density of the substance

    Returns
    -------
    Volume of the substance 
        m^3
    """

    return (mass * .001) / density