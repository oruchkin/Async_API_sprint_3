import datetime
import random
import uuid
from typing import cast
from unittest.mock import AsyncMock, Mock, patch

from faker import Faker
from fastapi import UploadFile
from src.db.base_provider import BaseProvider
from src.models.file_model import FileDbModel
from src.services.file_service import FileService
from src.services.minio_service import MinioStorage
from starlette.responses import StreamingResponse

fake = Faker()

mime_types = ["audio/mpeg", "audio/ogg", "video/mp4", "video/x-msvideo", "video/quicktime"]


async def test_upload_file() -> None:
    datetime_mock = Mock(wraps=datetime.datetime)
    datetime_mock.now.return_value = datetime.datetime(1999, 1, 1)
    bucket = "mybucket"
    with patch("datetime.datetime", new=datetime_mock):

        mock_db = AsyncMock(spec=BaseProvider)
        mock_storage = AsyncMock(spec=MinioStorage)
        mock_upload_file = AsyncMock(spec=UploadFile)

        file_mime_type = "audio/mpeg"
        mock_upload_file.filename = fake.file_name(extension=file_mime_type.split("/")[-1])
        mock_upload_file.content_type = file_mime_type
        mock_upload_file.size = fake.random_number(digits=6)

        file_service = FileService(db=mock_db, storage=mock_storage)

        await file_service.upload_file(file=mock_upload_file, bucket=bucket)

        mock_storage.save.assert_called_once()
        mock_db.add.assert_called_once()
        model = cast(FileDbModel, mock_db.add.call_args[0][0])
        assert model.path_in_storage.startswith("uploads/1999Q1/")


async def test_download_file() -> None:
    mock_db = AsyncMock(spec=BaseProvider)
    mock_storage = AsyncMock(spec=MinioStorage)
    file_service = FileService(db=mock_db, storage=mock_storage)

    file_db = FileDbModel(
        path_in_storage=f"uploads/{fake.file_name()}",
        filename=fake.file_name(),
        short_name=str(uuid.uuid4()),
        size=fake.random_number(digits=6),
        file_type=random.choice(mime_types),
        bucket="mybucket",
    )

    mock_db.find_by_shortname.return_value = file_db

    mock_storage.get_file.return_value = StreamingResponse(iter([b"test data"]))

    result = await file_service.download_file(short_name=file_db.short_name)

    mock_storage.get_file.assert_called_once_with(file_db.bucket, file_db.path_in_storage)
    assert isinstance(result, StreamingResponse)


async def test_delete_file() -> None:
    file_db = FileDbModel(
        path_in_storage=f"uploads/{fake.file_name()}",
        filename=fake.file_name(),
        short_name=str(uuid.uuid4()),
        size=fake.random_number(digits=6),
        file_type=random.choice(mime_types),
        bucket="mybucket",
    )

    mock_db = AsyncMock(spec=BaseProvider)
    mock_db.find_by_shortname.return_value = file_db

    mock_storage = AsyncMock(spec=MinioStorage)
    file_service = FileService(db=mock_db, storage=mock_storage)

    # act
    await file_service.delete_file(short_name=file_db.short_name)

    # assert
    mock_storage.delete.assert_called_once_with("mybucket", file_db.path_in_storage)
    mock_db.delete.assert_called_once_with(file_db)
