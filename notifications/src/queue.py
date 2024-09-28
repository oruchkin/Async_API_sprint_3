import asyncio
import logging

from src.db.rabbitmq import default_queue, rabbit_router
from src.models.queue_payload import QueuePayload

logger = logging.getLogger(__name__)


@rabbit_router.subscriber(queue=default_queue)
async def handle_rabbit_message(payload: QueuePayload):
    # Asynchronous handling of the message
    logger.info(f"Received message: {payload.message.id}")
    print(f"Received message: {payload.message.id}")
    # Simulate async processing
    await asyncio.sleep(1)
    print("Message processed")
