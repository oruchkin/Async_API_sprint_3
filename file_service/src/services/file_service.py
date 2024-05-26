from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import UploadFile, HTTPException
from starlette.responses import StreamingResponse

from src.services.minio_service import MinioStorage
from src.models.file_model import FileDbModel
import shortuuid
import os
import logging

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self, db: AsyncSession, storage: MinioStorage):
        self.db = db
        self.storage = storage

    async def upload_file(self,
                          file: UploadFile,
                          bucket: str,
                          path: str) -> FileDbModel:
        """ Upload a file to the storage. """
        base_name, file_extension = os.path.splitext(path)
        new_path = await self.generate_unique_path(self.db, base_name, file_extension)

        try:
            await self.storage.save(file, bucket, new_path)

            file_db = FileDbModel(
                path_in_storage=new_path,
                filename=file.filename,
                short_name=shortuuid.uuid(),
                size=file.size,
                file_type=file.content_type,
                bucket=bucket,
            )
            self.db.add(file_db)
            await self.db.commit()
            await self.db.refresh(file_db)
            return file_db

        except Exception as e:
            await self.db.rollback()
            logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while uploading the file.")

    async def download_file(self, bucket, short_name: str) -> StreamingResponse:
        """ Download a file from the storage by its short_name. """
        result = await self.db.execute(select(FileDbModel).filter_by(short_name=short_name, bucket=bucket))
        file_db = result.scalars().first()
        if not file_db:
            raise HTTPException(status_code=404, detail="File not found")
        return await self.storage.get_file("mybucket", file_db.path_in_storage)

    async def delete_file(self, bucket: str, short_name: str) -> None:
        """ Delete a file from the storage and the database by its short_name. """
        result = await self.db.execute(select(FileDbModel)
                                       .filter_by(short_name=short_name, bucket=bucket))
        file_db = result.scalars().first()
        if not file_db:
            raise HTTPException(status_code=404, detail="File not found")

        try:
            await self.storage.delete(file_db.bucket, file_db.path_in_storage)
            await self.db.delete(file_db)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"An error occurred while deleting the file: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while deleting the file.")

    async def file_exists(self, db: AsyncSession, path: str) -> bool:
        """ Check if a file with the specified path exists in the storage. """
        result = await db.execute(select(FileDbModel).filter_by(path_in_storage=path))
        file_db = result.first()
        return file_db is not None

    async def generate_presigned_url(self, bucket: str, short_name: str, expires_in: int = 3600) -> str:
        """ Generate a presigned URL for downloading the file. """
        result = await self.db.execute(select(FileDbModel).filter_by(short_name=short_name, bucket=bucket))
        file_db = result.scalars().first()
        if not file_db:
            raise HTTPException(status_code=404, detail="File not found")
        return await self.storage.generate_presigned_url(bucket, file_db.path_in_storage, expires_in)

    async def generate_unique_path(self,
                                   db: AsyncSession,
                                   base_name: str,
                                   file_extension: str) -> str:
        """ Generate a unique path for a file with
         the same name already in the storage. """
        new_path = f"{base_name}{file_extension}"
        counter = 1
        while await self.file_exists(db, new_path):
            new_path = f"{base_name}_{counter}{file_extension}"
            counter += 1
        return new_path

    async def has_permission(self, short_name: str) -> bool:
        """ Future method for checking permissions."""
        return True
