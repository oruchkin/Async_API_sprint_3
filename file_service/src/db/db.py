from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.settings import settings


user = settings.POSTGRES_USER
password = settings.POSTGRES_PASSWORD
host = settings.POSTGRES_HOST
port = settings.POSTGRES_PORT
db = settings.POSTGRES_DB
db_driver = "postgresql+asyncpg"

POSTGRES_URL = f"{db_driver}://{user}:{password}@{host}:{port}/{db}"
engine = create_async_engine(POSTGRES_URL,
                             echo=settings.POSTGRES_QUERY_LOGGING)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
