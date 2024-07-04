import uvicorn
from api.v1 import roles, users
from core.errors_utils import error_to_json_response
from core.lifecycle import lifespan
from core.tracer import configure_tracer
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace

load_dotenv()

app = FastAPI(
    title="Identity Provider API",
    description="Authentication and authorization endpoints",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)
configure_tracer(app)


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, error: Exception):
    """
    Wraps api errors into the valid json responses
    """
    return error_to_json_response(error)


app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    return response


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = trace.get_current_span().get_span_context().trace_id
    response = await call_next(request)
    response.headers["X-Trace-Id"] = format(trace_id, "x")

    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
