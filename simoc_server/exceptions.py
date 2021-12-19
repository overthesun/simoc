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


class BadRegistration(GenericError):
    status_code = 409

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Error During Registration"
        super().__init__(message, status_code=status_code)


class InvalidLogin(GenericError):
    status_code = 401

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Error During Login"
        super().__init__(message, status_code=status_code)


class BadRequest(GenericError):
    status_code = 400

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Bad request."
        super().__init__(message, status_code=status_code)


class NotFound(GenericError):
    status_code = 404

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Not Found."
        super().__init__(message, status_code=status_code)


class Unauthorized(GenericError):
    status_code = 401

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Unauthorized."
        super().__init__(message, status_code=status_code)


class ServerError(GenericError):
    status_code = 500

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Internal server error."
        super().__init__(message, status_code=status_code)


class AgentModelInitializationError(ServerError):
    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Unknown error while initializing agent model."
        super().__init__(message, status_code=status_code)


class AgentInitializationError(ServerError):
    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Unknown error while initializing agent."
        super().__init__(message, status_code=status_code)


class AgentModelError(ServerError):
    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Unknown error in agent model."
        super().__init__(message, status_code=status_code)


class GameNotFoundException(ServerError):
    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Could not find requested game."
        super().__init__(message, status_code=status_code)
