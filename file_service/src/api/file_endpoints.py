from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from src.db.base_provider import BaseProvider
from src.db.db import get_db
from src.services.file_service import FileService
from src.services.minio_service import MinioStorage

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile, bucket: str = "mybucket", db: BaseProvider = Depends(get_db)):
    # TODO: bucket must be defined by the client id
    file_service = FileService(db, MinioStorage())
    result = await file_service.upload_file(file=file, bucket=bucket)
    return result


@router.get("/{short_name}")
async def download_file(short_name: str, db: BaseProvider = Depends(get_db)):
    file_service = FileService(db, MinioStorage())
    file_obj = await file_service.download_file(short_name)

    if not await file_service.has_permission(short_name):
        raise HTTPException(status_code=403, detail="Access forbidden")

    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    return file_obj


@router.delete("/{short_name}", summary="Delete file", description="Delete file from S3 storage and database")
async def delete_file(short_name: str, db: BaseProvider = Depends(get_db)):
    file_service = FileService(db, MinioStorage())

    if not await file_service.has_permission(short_name):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Access forbidden")

    await file_service.delete_file(short_name)
    return {"detail": "File successfully deleted"}


@router.get(
    "/{short_name}/presigned_url/",
    summary="Generate presigned URL",
    description="Generate presigned URL for downloading the file",
)
async def generate_presigned_url(short_name: str, expires_in: int = 3600, db: BaseProvider = Depends(get_db)):
    file_service = FileService(db, MinioStorage())

    if not await file_service.has_permission(short_name):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Access forbidden")

    presigned_url = await file_service.generate_presigned_url(short_name, expires_in)
    return {"presigned_url": presigned_url}


@router.get(
    "/{short_name}/redirect_download/",
    summary="Redirect to presigned URL",
    description="Redirect the user to the presigned URL for downloading the file",
)
async def redirect_download(short_name: str, expires_in: int = 3600, db: BaseProvider = Depends(get_db)):
    file_service = FileService(db, MinioStorage())

    if not await file_service.has_permission(short_name):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Access forbidden")

    presigned_url = await file_service.generate_presigned_url(short_name, expires_in)
    return RedirectResponse(url=presigned_url)
