import logging.config
from contextlib import asynccontextmanager

from core.settings import KeycloakSettings
from fastapi import FastAPI
from jwcrypto.jwt import JWT
from services.keycloak_client import KeycloackClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для установления соединения с базами данных.
    Запускается при старте и закрывает соединения при завершении работы приложения.
    """

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    provider = JWT()
    provider.deserialize(token, key=None)
    print(provider.token)

    # settings = KeycloakSettings()
    # client = KeycloackClient(settings)
    # # testing Keycloak client
    # # await client.create_role("blablabla")
    # users = await client.list_users()
    # roles = await client.list_roles()
    # await client.set_user_role(users[-2].id, roles[1])
    # # await client.create_user("jonny4@example.com", "sample-password123")
    # token = await client.authenticate("jonny4@example.com", "sample-password123")
    # refreshed = await client.refresh(token.refresh_token)

    yield

    logger.info("Закрываем соеденения.")
