from pika import ConnectionParameters, PlainCredentials
from src.core.settings import RabbitMQSettings


def get_rabbitmq_params() -> ConnectionParameters:
    settings = RabbitMQSettings()
    credentials = PlainCredentials(settings.login, settings.password)
    return ConnectionParameters(host=settings.host, credentials=credentials)
