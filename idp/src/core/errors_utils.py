from http import HTTPStatus

import services.errors as errors
from aiohttp import ClientConnectorError
from fastapi.responses import JSONResponse


def error_to_json_response(error: Exception) -> JSONResponse:
    if isinstance(error, errors.NotAuthorizedError):
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={"message": error.message},
        )

    if isinstance(error, errors.NotFoundError):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"message": error.message},
        )

    if isinstance(error, errors.ValidationError):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"message": error.message},
        )

    if isinstance(error, ClientConnectorError):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"message": "Connectivity issue... Something is down"},
        )

    return JSONResponse(
        status_code=418,
        content={"message": "Something went wrong... it's time to check the logs"},
    )
