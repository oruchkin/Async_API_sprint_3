from miniopy_async import Minio
from miniopy_async.helpers import ObjectWriteResult
from fastapi import UploadFile
from src.core.settings import settings
from aiohttp import ClientSession
from starlette.responses import StreamingResponse
import datetime


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )

    async def save(self, file: UploadFile, bucket: str, path: str) -> ObjectWriteResult:
        result = await self.client.put_object(
            bucket_name=bucket, object_name=path, data=file.file, length=-1, part_size=10 * 1024 * 1024,
        )
        return result

    async def get_file(self, bucket: str, path: str) -> StreamingResponse:
        async with ClientSession() as session:
            response = await self.client.get_object(bucket, path, session)
            return StreamingResponse(
                response.content.iter_chunked(1024),
                media_type='application/octet-stream',
                headers={'Content-Disposition': f'attachment; filename="{path.split("/")[-1]}"'}
            )

    async def delete(self, bucket: str, path: str) -> None:
        await self.client.remove_object(bucket, path)

    async def generate_presigned_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for the given object."""
        expires = datetime.timedelta(seconds=expires_in)
        url = await self.client.presigned_get_object(bucket, path, expires=expires)
        return url
