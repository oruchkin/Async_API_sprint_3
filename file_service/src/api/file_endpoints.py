from fastapi import APIRouter, HTTPException, Depends, UploadFile
from src.db.db import get_db
from src.services.file_service import FileService
from src.services.minio_service import MinioStorage
import shortuuid
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile,
                      bucket: str = "mybucket",
                      db: AsyncSession = Depends(get_db)):
    file_service = FileService(db, MinioStorage())
    result = await file_service.upload_file(
        file=file,
        bucket=bucket,
        path=f"uploads/{file.filename}"
    )
    return result


@router.get("/download/{short_name}")
async def download_file(short_name: str,
                        bucket: str = "mybucket",
                        db: AsyncSession = Depends(get_db)):
    file_service = FileService(db, MinioStorage())
    file_obj = await file_service.download_file(bucket, short_name)

    if not await file_service.has_permission(short_name):
        raise HTTPException(status_code=403, detail="Access forbidden")

    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    return file_obj


@router.delete("/delete/{short_name}",
               summary="Delete file",
               description="Delete file from S3 storage and database")
async def delete_file(short_name: str,
                      bucket: str = "mybucket",
                      db: AsyncSession = Depends(get_db)):
    file_service = FileService(db, MinioStorage())

    if not await file_service.has_permission(short_name):
        raise HTTPException(status_code=403, detail="Access forbidden")

    await file_service.delete_file(bucket, short_name)
    return {"detail": "File successfully deleted"}


@router.get("/presigned_url/{bucket}/{short_name}",
            summary="Generate presigned URL",
            description="Generate presigned URL for downloading the file")
async def generate_presigned_url(bucket: str,
                                 short_name: str,
                                 expires_in: int = 3600,
                                 db: AsyncSession = Depends(get_db)):
    file_service = FileService(db, MinioStorage())

    if not await file_service.has_permission(short_name):
        raise HTTPException(status_code=403, detail="Access forbidden")

    presigned_url = await file_service.generate_presigned_url(bucket, short_name, expires_in)
    return {"presigned_url": presigned_url}
