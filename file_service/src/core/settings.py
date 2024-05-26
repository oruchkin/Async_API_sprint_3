import os


class Settings:
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "practicum")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "StrongPass")
    MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", False)

    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
    POSTGRES_DB = os.getenv("FASTAPI_POSTGRES_DB", "file_db")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_QUERY_LOGGING = os.getenv("FASTAPI_POSTGRES_QUERY_LOGGING", False)


settings = Settings()
