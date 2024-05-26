from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # PostgreSQL settings
    postgres_dbname: str = Field(..., alias="POSTGRES_DB")
    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(..., alias="POSTGRES_HOST")
    postgres_port: int = Field(..., alias="POSTGRES_PORT")

    # Elasticsearch settings
    elastic_url: str = Field(..., alias="ELASTIC_URL")
    elastic_index_name_movies: str = Field(default="movies", alias="ELASTIC_INDEX_NAME_MOVIES")
    elastic_index_name_genres: str = Field(default="genres", alias="ELASTIC_INDEX_NAME_GENRES")
    elastic_index_name_persons: str = Field(default="persons", alias="ELASTIC_INDEX_NAME_PERSONS")

    # General app settings
    initial_date: str = Field(default="1970-01-01", alias="INITIAL_DATE")
    delay: int = Field(default=10, alias="DELAY")

    state_file_path: str = Field(default="./etl_state.json", alias="STATE_FILE_PATH")

    max_attemts: int = 10
    border_sleep_time: int = 10
    factor: int = 2
    start_sleep_time: float = 0.1
