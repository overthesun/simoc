class AttributeDescriptor(object):

    def __init__(self, _type, is_client_attr, is_persisted_attr):
        self._type = _type
        self.is_client_attr = is_client_attr
        self.is_persisted_attr = is_persisted_attr

    def __repr__(self):
        return "type: {} is_client_attr: {} is_persisted_attr: {}".format(self._type,
                                                                          self.is_client_attr,
                                                                          self.is_persisted_attr)


class AttributeHolder(object):

    def __init__(self):
        self.attribute_descriptors = {}

    def _attr(self, name, default_value=None, _type=None, is_client_attr=True,
              is_persisted_attr=True):
        value_exists = name in self.__dict__.keys()

        if _type is None:
            if value_exists:
                _type = type(self.__dict__[name])
            else:
                _type = type(default_value)

        if not value_exists:
            self.__dict__[name] = default_value

        if name is None:
            raise Exception("'attribute' name cannot be equal to None.")
        self.attribute_descriptors[name] = AttributeDescriptor(_type, is_client_attr,
                                                               is_persisted_attr)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)
