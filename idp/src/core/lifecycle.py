import logging.config
from contextlib import asynccontextmanager

from core.settings import KeycloakSettings
from core.verification import verify_token
from fastapi import FastAPI
from services.keycloak_client import KeycloackClient
from jwcrypto.jwt import JWT

logger = logging.getLogger(__name__)
from src.services.keycloak_client import KeycloackClient, get_keycloak_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для установления соединения с базами данных.
    Запускается при старте и закрывает соединения при завершении работы приложения.
    """

    # settings = KeycloakSettings()
    # client = KeycloackClient(settings)
    # token_response = await client.authenticate("jonny4@example.com", "sample-password123")
    # payoad = await verify_token(client, token_response.access_token)
    # print(payoad["email"])

    keycloak = get_keycloak_service()
    await keycloak.oidc_discovery()

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    provider = JWT()
    provider.deserialize(token, key=None)
    print(provider.token)


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
