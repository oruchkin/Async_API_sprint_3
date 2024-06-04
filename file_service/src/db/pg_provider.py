from db.base_provider import BaseProvider
from models.file_model import FileDbModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class PgProvider(BaseProvider):
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory: async_sessionmaker[AsyncSession] = session_factory

    async def add(self, file: FileDbModel) -> None:
        async with self._session_factory() as session:
            session.add(file)
            await session.commit()

    async def find_by_shortname(self, short_name: str) -> FileDbModel | None:
        async with self._session_factory() as session:
            stmt = select(FileDbModel).filter(FileDbModel.short_name == short_name)
            result = await session.scalars(stmt)
            return result.one_or_none()

    async def delete(self, file: FileDbModel) -> None:
        async with self._session_factory() as session:
            await session.delete(file)
