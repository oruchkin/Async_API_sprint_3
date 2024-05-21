import os

class Settings:
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "practicum")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "StrongPass")
    MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", False)

settings = Settings()
