import logging.config
from contextlib import asynccontextmanager

from core.settings import KeycloakSettings
from fastapi import FastAPI
from services.keycloak_client import KeycloackClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для установления соединения с базами данных.
    Запускается при старте и закрывает соединения при завершении работы приложения.
    """
    settings = KeycloakSettings()
    client = KeycloackClient(settings)
    # testing Keycloak client
    all_users = await client.list_users()
    print(len(all_users))

    yield

    logger.info("Закрываем соеденения.")
