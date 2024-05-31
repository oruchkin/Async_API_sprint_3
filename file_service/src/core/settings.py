from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="practicum", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="StrongPass", env="MINIO_SECRET_KEY")
    MINIO_USE_SSL: bool = Field(default=False, env="MINIO_USE_SSL")

    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(default="user", env="POSTGRES_USER")
    POSTGRES_DB: str = Field(default="file_db", env="FASTAPI_POSTGRES_DB")
    POSTGRES_PASSWORD: str = Field(default="password", env="POSTGRES_PASSWORD")
    POSTGRES_QUERY_LOGGING: bool = Field(default=False, env="FASTAPI_POSTGRES_QUERY_LOGGING")


settings = Settings()
