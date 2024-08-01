from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_")
    # Broker endpoint must exactly match ip or hostname
    ensure_topics: bool = False
    server: str = "kafka-0:9092"
    client_id: str = "ugc-api"
