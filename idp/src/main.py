import uvicorn
from api.v1 import roles, users
from core.errors_utils import error_to_json_response
from core.lifecycle import lifespan
from dotenv import load_dotenv
from fastapi import FastAPI, Request

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
    """
    Wraps api errors into the valid json responses
    """
    return error_to_json_response(error)


app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
