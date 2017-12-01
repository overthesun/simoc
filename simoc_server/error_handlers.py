from flask import jsonify
from simoc_server import app

class GenericError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super(GenericError, self).__init__()
        if status_code is not None:
            self.status_code =  status_code
        self.message = message

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
        super(BadRegistration, self).__init__(message, status_code=status_code)

class InvalidLogin(GenericError):
    status_code = 409

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Error During Login"
        super(InvalidLogin, self).__init__(message, status_code=status_code)

class BadRequest(GenericError):
    status_code = 400

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Bad request."
        super(BadRequest, self).__init__(message, status_code=status_code)

class NotFound(GenericError):
    status_code = 404

    def __init__(self, message=None, status_code=None):
        if message is None:
            message = "Not Found."
        super(NotFound, self).__init__(message, status_code=status_code)

@app.errorhandler(GenericError)
def handle_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response