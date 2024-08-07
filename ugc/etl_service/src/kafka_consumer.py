from kafka import KafkaConsumer
import json
from transformers import transform_data
from clickhouse_client import ClickHouseClient
import logging


class KafkaConsumerService:
    def __init__(self, kafka_server: str, clickhouse_server: str, topic: str, group_id: str):
        self.kafka_consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_server,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            group_id=group_id
        )
        self.clickhouse_client = ClickHouseClient(clickhouse_server)
        logging.basicConfig(level=logging.INFO)

    def consume_messages(self):
        max_messages_to_fetch = 100000

        while True:
            raw_messages = self.kafka_consumer.poll(timeout_ms=1000, max_records=max_messages_to_fetch)
            messages = []

            for topic_partition, messages_batch in raw_messages.items():
                for message in messages_batch:
                    data = json.loads(message.value.decode('utf-8'))
                    logging.info(f"Received data from kafka: {data}")
                    transformed_data = transform_data(data)
                    messages.append(transformed_data)

            if messages:
                self.clickhouse_client.insert_data(messages)
                self.kafka_consumer.commit()

    def consume_messages_old_way(self):
        messages = []
        batch_to_insert_db = 5

        for message in self.kafka_consumer:
            data = json.loads(message.value.decode('utf-8'))
            logging.info(f"Received data from kafka: {data}")
            transformed_data = transform_data(data)

            messages.append(transformed_data)

            if len(messages) >= batch_to_insert_db:
                self.clickhouse_client.insert_data(messages)
                self.kafka_consumer.commit()
                messages = []
