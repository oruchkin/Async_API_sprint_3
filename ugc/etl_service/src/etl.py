import logging
import os

from kafka_consumer import KafkaConsumerService

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Etl services successfully started")

    kafka_server = os.getenv('KAFKA_SERVER', 'kafka-0:9094')
    clickhouse_server = os.getenv('CLICKHOUSE_SERVER', 'clickhouse')

    topic = 'movies_progress'
    group_id = 'etl-group'

    consumer_service = KafkaConsumerService(kafka_server, clickhouse_server, topic, group_id)
    consumer_service.consume_messages()
