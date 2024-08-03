import logging

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from models.movie_progress import MovieProgress

from .kafka_settings import KafkaSettings


class KafkaClient:
    _settings: KafkaSettings
    _logger: logging.Logger
    _topics: list[str]
    _producer: KafkaProducer

    def __init__(self, settings: KafkaSettings):
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._topics = []
        self._producer = KafkaProducer(bootstrap_servers=settings.server)

    def post_movie_progress(self, data: MovieProgress) -> None:
        """
        Sends model to the Kafka topic
        """
        self.ensure_topic("movies_progress")
        payload = data.model_dump_json().encode("utf-8")
        self._producer.send(topic="movies_progress", value=payload)
        self._producer.flush(timeout=10)  # this forcibly sends any messages that are stuck.
        self._producer.close(timeout=5)

    def ensure_topic(self, topic_name: str) -> None:
        if not self._settings.ensure_topics or topic_name in self._topics:
            return

        # How to properly configure endpoints
        # https://github.com/dpkp/kafka-python/issues/2093
        admin_client = KafkaAdminClient(
            bootstrap_servers=self._settings.server, api_version=(0, 10, 2), client_id=self._settings.client_id
        )
        self._topics = admin_client.list_topics()
        if topic_name not in self._topics:
            self._logger.info("Creating topic %s", topic_name)
            topic_list = []
            topic_list.append(NewTopic(name=topic_name, num_partitions=3, replication_factor=3))
            try:
                admin_client.create_topics(new_topics=topic_list)
            except TopicAlreadyExistsError:
                pass  # ignore it
            self._topics.append(topic_name)
        else:
            self._logger.info("Topic %s already exists", topic_name)
