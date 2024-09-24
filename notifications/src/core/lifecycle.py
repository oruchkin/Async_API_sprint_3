import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.core.queue_listener import rabbit_broker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для установления соединения с базами данных.
    Запускается при старте и закрывает соединения при завершении работы приложения.
    """
    await rabbit_broker.connect()

    result = await rabbit_broker.publish("Hi there", queue="hello_default")
    logger.info(result.delivery)

    yield

    await rabbit_broker.close()
