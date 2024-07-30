import logging

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from .kafka_settings import KafkaSettings


class KafkaClient:
    _settings: KafkaSettings
    _logger: logging.Logger
    _topics: list[str]

    def __init__(self, settings: KafkaSettings):
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._topics = []

    def ensure_topic(self, topic_name: str) -> None:
        if not self._settings.ensure_topics or topic_name in self._topics:
            return

        # How to properly configure endpoints
        # https://github.com/dpkp/kafka-python/issues/2093
        admin_client = KafkaAdminClient(
            bootstrap_servers=self._settings.broker, api_version=(0, 10, 2), client_id=self._settings.client_id
        )
        topics = admin_client.list_topics()
        if topic_name not in topics:
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
