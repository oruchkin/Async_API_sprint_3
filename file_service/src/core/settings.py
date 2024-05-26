import os


class Settings:
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "practicum")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "StrongPass")

    POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql+asyncpg://user:password@localhost:5432/file_db")
    POSTGRES_QUERY_LOGGING = os.getenv("POSTGRES_QUERY_LOGGING", False)
    MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", False)


settings = Settings()
