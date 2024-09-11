from fastapi import APIRouter, Depends
from src.services.idp_client import get_idp_client

router = APIRouter()


@router.post("/", summary="Добавляем событие")
async def add_event(idp=Depends(get_idp_client)) -> None:
    pass
