import logging.config
import os
import secrets
import string

import sentry_sdk
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from src.api.v1 import (
    films,
    films_rating,
    films_reviews,
    genres,
    health,
    persons,
    user_bookmarks,
)
from src.core.lifecycle import lifespan
from src.core.logger import LOGGING
from src.core.tracer import configure_tracer

load_dotenv()
logging.config.dictConfig(LOGGING)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


if sentry_dsn := os.getenv("FASTAPI_SENTRY_DSN"):
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    log_config=LOGGING,
    log_level=logging.DEBUG,
)


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
        logger.warn("Trace not capturing, check middleware sequence")
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


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(films_rating.router, prefix="/api/v1/films/rating", tags=["films"])
app.include_router(films_reviews.router, prefix="/api/v1/films/reviews", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(user_bookmarks.router, prefix="/api/v1/user/bookmarks", tags=["user", "bookmarks"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
