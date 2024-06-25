from http import HTTPStatus

import services.errors as errors
from fastapi import HTTPException


def handle_keycloak_error(error: errors.KeycloakError) -> HTTPException:
    if isinstance(error, errors.NotAuthorizedError):
        return HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=error.message)

    if isinstance(error, errors.NotFoundError):
        return HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error.message)

    if isinstance(error, errors.ValidationError):
        return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error.message)
