import uvicorn
from api.v1 import index
from fastapi import FastAPI

app = FastAPI(
    title="Identity Provider API",
    description="Authentication and authorization endpoints",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

app.include_router(index.router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
