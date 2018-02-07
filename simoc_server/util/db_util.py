

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