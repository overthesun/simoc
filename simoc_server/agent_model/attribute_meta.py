class AttributeDescriptor(object):

    def __init__(self, _type, is_client_attr, is_persisted_attr):
        self._type = _type
        self.is_client_attr = is_client_attr
        self.is_persisted_attr = is_persisted_attr

    def __repr__(self):
        return "type: {} is_client_attr: {} is_persisted_attr: {}".format(self._type, self.is_client_attr, self.is_persisted_attr)

class AttributeHolder(object):

    def __init__(self):
        self.attribute_descriptors = {}

    def _attr(self, name, default_value=None, _type=None, is_client_attr=True, is_persisted_attr=True):
        if _type is None:
            _type = type(default_value)

        if(name not in self.__dict__.keys()):
            self.__dict__[name] = default_value

        self.attribute_descriptors[name] = AttributeDescriptor(_type, is_client_attr, is_persisted_attr)
