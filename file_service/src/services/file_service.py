import datetime
import logging
import math
import os
import uuid
from http import HTTPStatus

import shortuuid
from fastapi import HTTPException, UploadFile
from src.db.base_provider import BaseProvider
from src.models.file_model import FileDbModel
from src.services.minio_service import MinioStorage
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self, db: BaseProvider, storage: MinioStorage):
        self._db = db
        self.storage = storage

    async def upload_file(self, file: UploadFile, bucket: str) -> FileDbModel:
        """Upload a file to the storage."""

        if not file.filename:
            raise ValueError("File name is required")

        if not file.size:
            raise ValueError("File size is required")

        if not file.content_type:
            raise ValueError("File content type is required")

        full_path = FileService._construct_file_path(file.filename)
        try:
            await self.storage.save(file, bucket, full_path)

            file_db = FileDbModel(
                path_in_storage=full_path,
                filename=file.filename,
                short_name=shortuuid.uuid(),
                size=file.size,
                file_type=file.content_type,
                bucket=bucket,
            )
            await self._db.add(file_db)
            return file_db

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An error occurred while uploading the file."
            )

    async def download_file(self, short_name: str) -> StreamingResponse:
        """
        Download a file from the storage by its short_name.
        """
        if file_db := await self._db.find_by_shortname(short_name):
            stream: StreamingResponse = await self.storage.get_file(file_db.bucket, file_db.path_in_storage)
            return stream

        raise HTTPException(status_code=404, detail="File not found")

    async def delete_file(self, short_name: str) -> None:
        """Delete a file from the storage and the database by its short_name."""
        if file_db := await self._db.find_by_shortname(short_name):
            try:
                await self.storage.delete(file_db.bucket, file_db.path_in_storage)
                await self._db.delete(file_db)
            except Exception as e:
                logger.error(f"An error occurred while deleting the file: {e}")
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the file."
                )
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="File not found")

    async def generate_presigned_url(self, short_name: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for downloading the file."""
        if file_db := await self._db.find_by_shortname(short_name):
            return await self.storage.generate_presigned_url(file_db.bucket, file_db.path_in_storage, expires_in)

        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="File not found")

    async def has_permission(self, short_name: str) -> bool:
        """Future method for checking permissions."""
        return True

    @staticmethod
    def _construct_file_path(file_name: str) -> str:

        id = uuid.uuid4()
        now = datetime.datetime.now()
        _, file_extension = os.path.splitext(file_name)
        dt = str(now.year) + "Q" + str(math.ceil(now.month / 4))
        full_path = f"uploads/{dt}/{str(id)}{file_extension}"
        return full_path
