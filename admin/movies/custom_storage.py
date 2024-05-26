import requests
from config import settings
from django.core.files.storage import Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.deconstruct import deconstructible


@deconstructible
class CustomStorage(Storage):
    def __init__(self) -> None:
        super().__init__()
        base_url = settings.FILE_STORAGE_URL  # type: ignore
        self._upload_url = f"{base_url}/api/files/upload"
        self._file_url = f"{base_url}/api/files/download_stream"

    def _save(self, name, content: InMemoryUploadedFile):
        endpoint = f"{self._upload_url}?bucket={settings.FILE_STORAGE_BUCKET}"  # type: ignore
        response = requests.post(endpoint, files={"file": (content.name, content, content.content_type)})
        # предполагается, что от сервиса приходит json-объект, содержащий поле 'short_name' с коротким именем файла
        data = response.json()
        return data.get("short_name")

    def url(self, name):
        return f"{self._file_url}/{name}"

    def exists(self, name):
        return False
