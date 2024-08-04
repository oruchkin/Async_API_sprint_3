from kafka import KafkaConsumer
import json
from transformers import transform_data
from clickhouse_client import ClickHouseClient

class KafkaConsumerService:
    def __init__(self, kafka_server, topic, group_id):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_server,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id
        )
        self.clickhouse_client = ClickHouseClient()

    def consume_messages(self):
        for message in self.consumer:
            data = json.loads(message.value.decode('utf-8'))
            transformed_data = transform_data(data)
            print("transformed_data")
            print(transformed_data)
            self.clickhouse_client.insert_data(transformed_data)
