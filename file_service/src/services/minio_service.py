import datetime

from aiohttp import ClientSession
from fastapi import UploadFile
from miniopy_async import Minio
from miniopy_async.helpers import ObjectWriteResult
from src.core.settings import minio_settings
from starlette.responses import StreamingResponse


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            endpoint=minio_settings.endpoint,
            access_key=minio_settings.access_key,
            secret_key=minio_settings.secret_key,
            secure=minio_settings.use_ssl,
        )

    async def save(self, file: UploadFile, bucket: str, path: str) -> ObjectWriteResult:
        result = await self.client.put_object(
            bucket_name=bucket,
            object_name=path,
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )
        return result

    async def get_file(self, bucket: str, path: str) -> StreamingResponse:
        async with ClientSession() as session:
            response = await self.client.get_object(bucket, path, session)
            return StreamingResponse(
                response.content.iter_chunked(1024),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f'attachment; filename="{path.split("/")[-1]}"'},
            )

    async def delete(self, bucket: str, path: str) -> None:
        await self.client.remove_object(bucket, path)

    async def generate_presigned_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for the given object."""
        expires = datetime.timedelta(seconds=expires_in)
        url: str = await self.client.presigned_get_object(bucket, path, expires=expires)
        return url
