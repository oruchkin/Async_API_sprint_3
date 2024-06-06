from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MINIO_")
    endpoint: str = ""
    access_key: str = ""
    secret_key: str = ""
    use_ssl: bool = False


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")
    host: str = ""
    port: int = 0
    user: str = ""
    password: str = ""

    def get_url(self, db: str) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{db}"


class FileapiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FILEAPI_")
    postgres_db: str = ""
    postgres_query_logging: bool = False


minio_settings = MinioSettings()

postgres_settings = PostgresSettings()

fileapi_settings = FileapiSettings()
