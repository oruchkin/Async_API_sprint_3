import random
from unittest.mock import AsyncMock, MagicMock
import pytest
from faker import Faker
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse
import uuid
from src.models.file_model import FileDbModel
from src.services.file_service import FileService
from src.services.minio_service import MinioStorage

fake = Faker()

mime_types = ["audio/mpeg", "audio/ogg", "video/mp4", "video/x-msvideo", "video/quicktime"]

@pytest.mark.asyncio
async def test_upload_file():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_storage = AsyncMock(spec=MinioStorage)
    mock_upload_file = AsyncMock(spec=UploadFile)

    file_mime_type = random.choice(mime_types)
    mock_upload_file.filename = fake.file_name(extension=file_mime_type.split("/")[-1])
    mock_upload_file.content_type = file_mime_type
    mock_upload_file.size = fake.random_number(digits=6)

    file_service = FileService(db=mock_db, storage=mock_storage)

    path = f"uploads/{mock_upload_file.filename}"

    file_service.generate_unique_path = AsyncMock(return_value=path)

    await file_service.upload_file(file=mock_upload_file, bucket="mybucket", path=mock_upload_file.filename)

    mock_storage.save.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_download_file():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_storage = AsyncMock(spec=MinioStorage)
    file_service = FileService(db=mock_db, storage=mock_storage)

    file_db = FileDbModel(
        path_in_storage=f"uploads/{fake.file_name()}",
        filename=fake.file_name(),
        short_name=str(uuid.uuid4()),
        size=fake.random_number(digits=6),
        file_type=random.choice(mime_types),
        bucket="mybucket"
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = file_db
    mock_db.execute.return_value = mock_result

    mock_storage.get_file.return_value = StreamingResponse(iter([b'test data']))

    result = await file_service.download_file(bucket="mybucket", short_name=file_db.short_name)

    mock_storage.get_file.assert_called_once_with("mybucket", file_db.path_in_storage)
    assert isinstance(result, StreamingResponse)

@pytest.mark.asyncio
async def test_delete_file():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_storage = AsyncMock(spec=MinioStorage)
    file_service = FileService(db=mock_db, storage=mock_storage)

    file_db = FileDbModel(
        path_in_storage=f"uploads/{fake.file_name()}",
        filename=fake.file_name(),
        short_name=str(uuid.uuid4()),
        size=fake.random_number(digits=6),
        file_type=random.choice(mime_types),
        bucket="mybucket"
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = file_db
    mock_db.execute.return_value = mock_result

    await file_service.delete_file(bucket="mybucket", short_name=file_db.short_name)

    mock_storage.delete.assert_called_once_with("mybucket", file_db.path_in_storage)
    mock_db.delete.assert_called_once_with(file_db)
    mock_db.commit.assert_called_once()
