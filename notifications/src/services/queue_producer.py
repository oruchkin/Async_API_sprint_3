import functools
import json
import logging

from fastapi import Depends
from pika import BasicProperties, ConnectionParameters, PlainCredentials
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType
from src.db.rabbitmq import get_rabbitmq_params


class QueueProducer:
    EXCHANGE = "text"
    EXCHANGE_TYPE = ExchangeType.topic
    PUBLISH_INTERVAL = 1
    QUEUE = "text"
    ROUTING_KEY = "hello_default"

    def __init__(self, params: ConnectionParameters):
        self._connection = None
        self._channel = None

        self._logger = logging.getLogger(__name__)

        self._deliveries: list[int] = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0

        self._stopping = False
        self._params = params

    def connect(self):
        self._logger.info("Connecting to %s", str(self._params))
        return AsyncioConnection(
            self._params,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed,
        )

    def on_connection_open(self, connection):
        self._logger.info("Connection opened")
        self._connection = connection
        self._logger.info("Creating a new channel")
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_open_error(self, _unused_connection, err):
        self._logger.error("Connection open failed: %s", err)

    def on_connection_closed(self, _unused_connection, reason):
        self._logger.warning("Connection closed: %s", reason)
        self._channel = None

    def on_channel_open(self, channel):
        self._logger.info("Channel opened")
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        self._logger.info("Adding channel close callback")
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        self._logger.warning("Channel %i was closed: %s", channel, reason)
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def setup_exchange(self, exchange_name):
        self._logger.info("Declaring exchange %s", exchange_name)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(exchange=exchange_name, exchange_type=self.EXCHANGE_TYPE, callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        self._logger.info("Exchange declared: %s", userdata)
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        self._logger.info("Declaring queue %s", queue_name)
        self._channel.queue_declare(queue=queue_name, callback=self.on_queue_declareok)

    def on_queue_declareok(self, _unused_frame):
        self._logger.info("Binding %s to %s with %s", self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        self._channel.queue_bind(self.QUEUE, self.EXCHANGE, routing_key=self.ROUTING_KEY, callback=self.on_bindok)

    def on_bindok(self, _unused_frame):
        self._logger.info("Queue bound")
        self.start_publishing()

    def start_publishing(self):
        self._logger.info("Issuing Confirm.Select RPC command")
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split(".")[1].lower()
        self._logger.info("Received %s for delivery tag: %i", confirmation_type, method_frame.method.delivery_tag)
        if confirmation_type == "ack":
            self._acked += 1
        elif confirmation_type == "nack":
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        self._logger.info(
            "Published %i messages, %i have yet to be confirmed, " "%i were acked and %i were nacked",
            self._message_number,
            len(self._deliveries),
            self._acked,
            self._nacked,
        )

    def publish_message(self, message):
        if self._channel is None or not self._channel.is_open:
            return

        hdrs = {"a": "b"}
        properties = BasicProperties(app_id="example-publisher", content_type="application/json", headers=hdrs)

        # self._channel.basic_publish(
        #     self.EXCHANGE, self.ROUTING_KEY, json.dumps(message, ensure_ascii=False), properties
        # )
        self._channel.basic_publish("", "hello_default", json.dumps(message, ensure_ascii=False))
        self._message_number += 1
        self._deliveries.append(self._message_number)
        self._logger.info("Published message # %i", self._message_number)


def get_queue_producer(mq_params=Depends(get_rabbitmq_params)) -> QueueProducer:
    return QueueProducer(mq_params)
