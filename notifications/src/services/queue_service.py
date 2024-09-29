import logging
from typing import Annotated

from fastapi import Depends
from faststream.rabbit.fastapi import RabbitBroker
from src import models
from src.db.rabbitmq import default_queue, get_rabbitmq_broker, sent_notifications_queue


class QueueService:
    def __init__(self, queue: RabbitBroker):
        self._queue = queue
        self._logger = logging.getLogger(__name__)

    async def publish_notification(self, notification: models.Notification) -> None:
        payload = models.QueuePayload(message=notification)
        status = await self._queue.publish(payload.model_dump(), queue=default_queue)
        self._logger.info(status)

    async def publish_sent_notification(self, notification: models.NotificationSent) -> None:
        payload = models.NotificationSentQueuePayload(message=notification)
        status = await self._queue.publish(payload.model_dump(), queue=sent_notifications_queue)
        self._logger.info(status)


def get_queue(rabbitmq: Annotated[RabbitBroker, Depends(get_rabbitmq_broker)]) -> QueueService:
    return QueueService(rabbitmq)
