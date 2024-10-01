from pydantic_settings import BaseSettings, SettingsConfigDict

NOTIFICATION_TIMEOUT_SEC = 60 * 5


class DjangoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADMIN_")
    s3_bucket: str = ""


class JaegerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JAEGER_")
    host: str
    port: int


class SMTPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SMTP_")
    host: str = ""
    port: int = 0
    login: str = ""
    password: str = ""


class IDPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IDP_")
    url: str = ""
    grpc: str = ""


class KeycloakSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IDP_KEYCLOAK_")
    url: str = ""
    client: str = ""


class RabbitMQSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RABBITMQ_")
    host: str = ""
    login: str = ""
    password: str = ""

    def create_url(self) -> str:
        return f"amqp://{self.login}:{self.password}@{self.host}:5672/"


class SendgridSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENDGRID_")
    enabled: bool = False
    api_key: str = ""
    sender: str = ""


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MONGO_")
    connection: str = ""
