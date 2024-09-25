import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from faststream.rabbit import RabbitBroker
from src.db.rabbitmq import default_queue, get_rabbitmq_broker

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/notify", summary="Отправляем нотификация")
async def do_notify(rabbitmq: Annotated[RabbitBroker, Depends(get_rabbitmq_broker)]) -> None:
    smth = await rabbitmq.publish({"m": {"key": "Hi there"}}, queue=default_queue)
    logger.info(smth)
