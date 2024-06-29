from http import HTTPStatus

import services.errors as errors
import uvicorn
from api.v1 import roles, users
from core.lifecycle import lifespan
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI(
    title="Identity Provider API",
    description="Authentication and authorization endpoints",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, error: Exception):
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

    return JSONResponse(
        status_code=418,
        content={"message": "Something went wrong... it's time to check the logs"},
    )


app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
