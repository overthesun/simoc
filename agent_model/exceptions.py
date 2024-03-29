class GenericError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__()
        if status_code is not None:
            self.status_code =  status_code
        self.message = message

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}({self.message!r}, {self.status_code})'
    __str__ = __repr__

    def to_dict(self):
        return {
            "error_type":self.__class__.__name__,
            "message":self.message
        }


class AgentModelInitializationError(GenericError):
    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Unknown error while initializing agent model."
        super().__init__(message, status_code=status_code)


class AgentInitializationError(GenericError):
    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Unknown error while initializing agent."
        super().__init__(message, status_code=status_code)


def _list_errors(e, stem=''):
    if len(e) == 0:
        return ''
    elif type(e) == dict:
        output = ''
        for k, v in e.items():
            output += _list_errors(v, stem + f'/{k}')
        return output
    else:
        return f'\n{stem}: {e} '

class AgentModelConfigError(GenericError):
    def __init__(self, errors, status_code=None):
        self.errors = errors
        super().__init__("", status_code=status_code)

    def __repr__(self):
        return _list_errors(self.errors, 'config')
    __str__ = __repr__


class AgentModelError(GenericError):
    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Unknown error in agent model."
        super().__init__(message, status_code=status_code)

