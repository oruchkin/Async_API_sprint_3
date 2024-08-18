import uvicorn
from fastapi import FastAPI
from src.api.file_endpoints import router as file_router

app = FastAPI(
    title="File storage API",
    description="Provides files storage functionality",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

app.include_router(file_router, prefix="/api/v1/files")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
