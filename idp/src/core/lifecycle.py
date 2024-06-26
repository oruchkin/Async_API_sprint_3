import logging.config
from contextlib import asynccontextmanager

from core.settings import KeycloakSettings
from core.verification import verify_token
from fastapi import FastAPI
from services.keycloack_endpoints import KeycloakEndpoints
from services.oidc_client import OIDCClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для установления соединения с базами данных.
    Запускается при старте и закрывает соединения при завершении работы приложения.
    """

    settings = KeycloakSettings()
    endpoints = KeycloakEndpoints(settings)
    oidc = OIDCClient(endpoints.base_url, settings)
    token_response = await oidc.password_flow("jonny4@example.com", "sample-password123")
    payoad = await verify_token(oidc, token_response.access_token)
    print(payoad["email"])

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
