import logging.config
import secrets
import string

import uvicorn
from api.v1 import films, genres, health, persons
from core.lifecycle import lifespan
from core.logger import LOGGING
from core.tracer import configure_tracer
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from opentelemetry import trace

load_dotenv()
logging.config.dictConfig(LOGGING)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

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
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
