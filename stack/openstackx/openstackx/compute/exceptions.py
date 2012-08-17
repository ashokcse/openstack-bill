class ComputeException(Exception):
    """
    The base exception class for all exceptions this library raises.
    """
    def __init__(self, code, message=None, details=None):
        self.code = code
        self.message = message or self.__class__.message
        self.details = details
        
    def __str__(self):
        return "%s (HTTP %s)" % (self.message, self.code)

class BadRequest(ComputeException):
    """
    HTTP 400 - Bad request: you sent some malformed data.
    """
    http_status = 400
    message = "Bad request"

class Unauthorized(ComputeException):
    """
    HTTP 401 - Unauthorized: bad credentials.
    """
    http_status = 401
    message = "Unauthorized"

class Forbidden(ComputeException):
    """
    HTTP 403 - Forbidden: your credentials don't give you access to this resource.
    """
    http_status = 403
    message = "Forbidden"
    
class NotFound(ComputeException):
    """
    HTTP 404 - Not found
    """
    http_status = 404
    message = "Not found"

class OverLimit(ComputeException):
    """
    HTTP 413 - Over limit: you're over the API limits for this time period.
    """
    http_status = 413
    message = "Over limit"

# In Python 2.4 Exception is old-style and thus doesn't have a __subclasses__()
# so we can do this:
#     _code_map = dict((c.http_status, c) for c in ComputeException.__subclasses__())
#
# Instead, we have to hardcode it:
_code_map = dict((c.http_status, c) for c in [BadRequest, Unauthorized, Forbidden, NotFound, OverLimit])

def from_response(response, body):
    """
    Return an instance of a ComputeException or subclass
    based on an httplib2 response. 
    
    Usage::
    
        resp, body = http.request(...)
        if resp.status != 200:
            raise exception_from_response(resp, body)
    """
    cls = _code_map.get(response.status, ComputeException)
    if body:
        error = body[body.keys()[0]]
        return cls(code=response.status, 
                   message=error.get('message', None),
                   details=error.get('details', None))
    else:
        return cls(code=response.status)