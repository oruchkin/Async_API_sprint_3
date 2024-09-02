from fastapi import APIRouter

router = APIRouter()


@router.post("/notify", summary="Отправляем нотификация")
async def do_notify() -> None:
    pass
