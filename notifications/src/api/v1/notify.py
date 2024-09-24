import logging

from fastapi import APIRouter
from faststream.rabbit import RabbitBroker
from src.core.settings import RabbitMQSettings

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/notify", summary="Отправляем нотификация")
async def do_notify() -> None:
    settings = RabbitMQSettings()
    queue_url = settings.create_url()
    rabbit_broker = RabbitBroker(queue_url, logger=logging.getLogger(__name__), log_level=logging.INFO)
    await rabbit_broker.connect()
    smth = await rabbit_broker.publish("Hi there", routing_key="hello_default")
    if smth and smth.delivery.reply_code:
        logger.warning(f"Failed {smth.delivery.reply_code} {smth.delivery.reply_text}")
