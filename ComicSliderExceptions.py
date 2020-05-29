class SeeOther(ValueError):
    def __init__(self, message):
        super(SeeOther, self).__init__("See Other: " + str(message))

class BadRequestError(ValueError):
    def __init__(self, message):
        super(BadRequestError, self).__init__("Bad Request: " + str(message))

class NotFoundError(ValueError):
    def __init__(self, message):
        super(NotFoundError, self).__init__("Not Found: " + str(message))

class InternalServerError(Exception):
    def __init__(self, message):
        super(InternalServerError, self).__init__("Internal Server Error: " + str(message))

class GatewayTimeoutError(Exception):
    def __init__(self, message):
        super(GatewayTimeoutError, self).__init__("Gateway Timeout Error: " + str(message))

class ForbiddenError(Exception):
    def __init__(self, message):
        super(ForbiddenError, self).__init__("Forbidden Error: " + str(message))