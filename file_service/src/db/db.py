from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.core.settings import fileapi_settings, postgres_settings

from .base_provider import BaseProvider
from .pg_provider import PgProvider

db = fileapi_settings.postgres_db

postgres_url = postgres_settings.get_url(db)
engine = create_async_engine(postgres_url, echo=fileapi_settings.postgres_query_logging)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> BaseProvider:
    provider = PgProvider(SessionLocal)
    return provider
