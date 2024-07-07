import uvicorn
from api.v1 import roles, users
from core.auth import BasicAuthBackend
from core.errors_utils import error_to_json_response
from core.lifecycle import lifespan
from db.redis import get_redis
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from services.throttling_service import ThrottlingService
from starlette.middleware.authentication import AuthenticationMiddleware

load_dotenv()

middleware = []

app = FastAPI(
    title="Identity Provider API",
    description="Authentication and authorization endpoints",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    middleware=middleware,
)


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, error: Exception):
    """
    Wraps api errors into the valid json responses
    """
    return error_to_json_response(error)


@app.middleware("http")
async def throttle_by_user(request: Request, call_next):

    if request.user.is_authenticated:
        # throttle here
        redis = get_redis()
        throttler = ThrottlingService(redis)
        if not await throttler.is_allowed(request.user):
            return ORJSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "That's too much, good luck in a minute"},
            )

    return await call_next(request)


app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
