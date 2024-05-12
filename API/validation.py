from werkzeug.exceptions import HTTPException , BadRequest
from werkzeug.sansio.response import Response

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)

