import logging

from faststream.rabbit import RabbitQueue
from faststream.rabbit.fastapi import RabbitBroker, RabbitRouter
from src.core.settings import RabbitMQSettings

logger = logging.getLogger(__name__)

settings = RabbitMQSettings()
queue_url = settings.create_url()
rabbit_router = RabbitRouter(queue_url)

default_queue = RabbitQueue("notifications_queue", durable=True)
sent_notifications_queue = RabbitQueue("notifications_sent_queue", durable=True)


def get_rabbitmq_broker() -> RabbitBroker:
    return rabbit_router.broker
