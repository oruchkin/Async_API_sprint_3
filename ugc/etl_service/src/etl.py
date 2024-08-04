import os
from kafka_consumer import KafkaConsumerService

if __name__ == "__main__":
    print("start")
    # kafka_server = os.getenv('KAFKA_SERVER', 'kafka-0:9094')
    kafka_server = "localhost:9094"
    topic = 'movies_progress'
    group_id = 'etl-group'

    consumer_service = KafkaConsumerService(kafka_server, topic, group_id)
    consumer_service.consume_messages()
