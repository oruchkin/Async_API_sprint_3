from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.settings import settings


engine = create_async_engine(settings.DATABASE_URL,
                             echo=settings.DB_QUERY_LOGGING)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
