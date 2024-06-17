import json
from httpx import HTTPError
from fastapi import HTTPException

# Exception class declarations
# All the error code other than 404/422 will be 500

class NotFoundException(Exception):
    pass


class UnprocessableEntityException(Exception):
    pass


class InternalServerException(Exception):
    pass


class TitleNotFoundException(Exception):
    pass


class CustomHTTPException(HTTPException):
    def __init__(self, title: str, detail: str, correlation_id: str, status_code: int = 400):
        error_response = {
            "errors": [
                {
                    "title": title,
                    "detail": detail,
                }
            ]
        }
        super().__init__(status_code=status_code, detail=error_response, headers={"X-Correlation-ID": correlation_id})


def handle_http_error(err: HTTPError, correlation_id: str,  default_detail='Internal Server Error'):
    """
    Handle HTTP errors and extract error details.

    Args:
        err (HTTPError): The HTTPError exception.
        default_detail (str): The default detail message.

    Returns:
        HTTPException: An HTTPException with the appropriate status code and detail message.
    """
    if hasattr(err, 'response') and err.response:
        try:
            err_response = err.response.json()
            detail = err_response.get('message', default_detail)
        except json.JSONDecodeError:
            detail = err.response.text
        status_code = err.response.status_code
    else:
        status_code = 500
        detail = default_detail

    return CustomHTTPException(status_code=status_code, detail=detail, correlation_id=correlation_id, title="error")
