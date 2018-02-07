


class AgentAttributeDescriptor(object):

    def __init__(self, _type, is_client_attr, is_persisted_attr):
        self._type = _type
        self.is_client_attr = is_client_attr
        self.is_persisted_attr = is_persisted_attr

    def __repr__(self):
        return "type: {} is_client_attr: {} is_persisted_attr: {}".format(self.type, self.is_client_attr, self.is_persisted_attr)

class AgentAttributeHolder(object):

    def _attr(self, name, value, _type=None, is_client_attr=True, is_persisted_attr=True):
        if _type is None:
            _type = type(value)

        self.__dict__[name] = value

        descr =  AgentAttributeDescriptor(_type, is_client_attr, is_persisted_attr)
        try:
            self.attribute_descriptors[name] = descr
        except AttributeError:
            # initialize if not already initialized
            self.attribute_descriptors = { name:descr }