import asyncio
import logging.config
import secrets
import string

import uvicorn
from core.auth import BasicAuthBackend
from core.errors_utils import error_to_json_response
from core.grpc import serve, start_grpc
from core.lifecycle import lifespan
from core.logger import LOGGING
from core.tracer import configure_tracer
from db.redis import get_redis
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from prometheus_fastapi_instrumentator import Instrumentator
from services.throttling_service import ThrottlingService
from starlette.middleware.authentication import AuthenticationMiddleware

from api.v1 import auth_google, auth_vk, roles, users

load_dotenv()
logging.config.dictConfig(LOGGING)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Identity Provider API",
    description="Authentication and authorization endpoints",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    log_config=LOGGING,
    log_level=logging.DEBUG,
)
Instrumentator().instrument(app).expose(app)


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


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    trace_id = trace.get_current_span().get_span_context().trace_id
    current_span = trace.get_current_span()
    if current_span.is_recording():
        current_span.set_attribute("http.request_id", request_id or "NA")
        response = await call_next(request)
        response.headers["X-Trace-Id"] = format(trace_id, "x")
        response.headers["X-Request-Id"] = request_id or "NA"
        return response
    else:
        logger.warning("Trace not capturing, check middleware sequence")
        return await call_next(request)


# middlewares are executed from the bottom to top
# enabled opentelemetry after we set Request-Id but before we are adding attributes
configure_tracer(app)


@app.middleware("http")
async def ensure_request_id_header(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        alphabet = string.ascii_letters + string.digits
        request_id = "".join(secrets.choice(alphabet) for i in range(16))
        headers = request.headers.mutablecopy()
        delattr(request, "_headers")
        headers["X-Request-Id"] = request_id
        request.scope["headers"] = headers.raw

    return await call_next(request)


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, error: Exception):
    """
    Wraps api errors into the valid json responses
    """
    return error_to_json_response(error)


app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(auth_vk.router, prefix="/api/v1/auth/vk", tags=["auth", "vk"])
app.include_router(auth_google.router, prefix="/api/v1/auth/google", tags=["auth", "google"])


async def start_fastapi():
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
    server = uvicorn.Server(config)
    await server.serve()


# Main function to run both servers
# God bless ChatGPT!
async def main():
    await asyncio.gather(
        start_fastapi(),
        start_grpc(),
    )


if __name__ == "__main__":
    asyncio.run(main())
