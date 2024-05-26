import logging
from typing import TypedDict

import requests
from config import settings
from django.core.files.storage import Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.deconstruct import deconstructible


class FileInfo(TypedDict):
    size: int
    path_in_storage: str
    id: str
    file_type: str
    created_at: str
    filename: str
    short_name: str
    bucket: str


logger = logging.getLogger(__name__)


@deconstructible
class CustomStorage(Storage):
    def __init__(self) -> None:
        super().__init__()
        base_url = settings.FILE_STORAGE_URL  # type: ignore
        self._upload_url = f"{base_url}/api/v1/files/upload"
        self._delete_url = f"{base_url}/api/v1/files/delete"
        self._file_url = f"{base_url}/api/v1/files/download_stream"

    def _save(self, name, content: InMemoryUploadedFile):
        endpoint = f"{self._upload_url}?bucket={settings.FILE_STORAGE_BUCKET}"  # type: ignore
        response = requests.post(endpoint, files={"file": (content.name, content, content.content_type)})
        data: FileInfo = response.json()
        return data.get("short_name")

    def url(self, name):
        return f"{self._file_url}/{name}"

    def exists(self, name):
        return False

    def delete(self, name):
        endpoint = f"{self._delete_url}?bucket={settings.FILE_STORAGE_BUCKET}&short_name={name}"  # type: ignore
        response = requests.delete(endpoint)
        data = response.json()
        logger.info("File deleted", data)
