from abc import ABCMeta, abstractmethod

class BaseDTO(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def get_state_diff(self, prev_state):
        pass


