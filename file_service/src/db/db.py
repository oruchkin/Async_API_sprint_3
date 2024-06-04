from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.core.settings import fileapi_settings, postgres_settings

from file_service.src.db.base_provider import BaseProvider
from file_service.src.db.pg_provider import PgProvider

user = postgres_settings.user
password = postgres_settings.password
host = postgres_settings.host
port = postgres_settings.port
db = fileapi_settings.postgres_db
db_driver = "postgresql+asyncpg"

POSTGRES_URL = f"{db_driver}://{user}:{password}@{host}:{port}/{db}"
engine = create_async_engine(POSTGRES_URL, echo=fileapi_settings.postgres_query_logging)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> BaseProvider:
    provider = PgProvider(SessionLocal)
    return provider
