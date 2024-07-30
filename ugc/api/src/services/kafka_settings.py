from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_")
    broker: str = "kafka-0:9092"
    ensure_topics: bool = False
    server: str = "host.docker.internal:9094"
    client_id: str = "ugc-api"
