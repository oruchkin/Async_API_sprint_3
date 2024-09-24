import asyncio
import logging

from faststream.rabbit import RabbitBroker, RabbitMessage
from src.core.settings import RabbitMQSettings

settings = RabbitMQSettings()
queue_url = settings.create_url()
rabbit_broker = RabbitBroker(queue_url, logger=logging.getLogger(__name__), log_level=logging.INFO)


@rabbit_broker.subscriber("hello_default")
async def handle_rabbit_message(message: RabbitMessage):
    # Asynchronous handling of the message
    logging.info(f"Received message: {message.body}")
    print(f"Received message: {message.body}")
    # Simulate async processing
    await asyncio.sleep(1)
    print("Message processed")
