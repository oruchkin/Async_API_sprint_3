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
        self._upload_url = f"{base_url}/api/v1/"
        self._file_url = f"{base_url}/api/v1/download_stream"

    def _save(self, name, content: InMemoryUploadedFile):
        r = requests.post(self._upload_url, files={"file": (content.name, content, content.content_type)})
        # предполагается, что от сервиса приходит json-объект, содержащий поле 'short_name' с коротким именем файла
        return r.json().get("short_name")

    def url(self, name):
        return f"{self._file_url}/{name}"

    def exists(self, name):
        return False
