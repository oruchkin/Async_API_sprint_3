import asyncio
import logging

from fastapi import FastAPI
from faststream.rabbit import RabbitQueue
from faststream.rabbit.fastapi import RabbitBroker, RabbitRouter
from pydantic import BaseModel
from src.core.settings import RabbitMQSettings

logger = logging.getLogger(__name__)

settings = RabbitMQSettings()
queue_url = settings.create_url()
rabbit_router = RabbitRouter(queue_url)

default_queue = RabbitQueue("hello_default", durable=True)


def get_rabbitmq_broker() -> RabbitBroker:
    return rabbit_router.broker


class Incoming(BaseModel):
    m: dict


@rabbit_router.subscriber(queue=default_queue)
async def handle_rabbit_message(message: Incoming):
    # Asynchronous handling of the message
    logging.info(f"Received message: {message}")
    print(f"Received message: {message}")
    # Simulate async processing
    await asyncio.sleep(1)
    print("Message processed")


@rabbit_router.after_startup
async def test(app: FastAPI):
    await rabbit_router.broker.publish({"m": {"key": "value"}}, queue=default_queue)
