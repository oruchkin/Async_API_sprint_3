import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from services.keycloak_client import KeycloackClient, get_keycloak_service
from services.oidc_client import get_oidc_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting...")

    oidc = get_oidc_service()
    keycloak: KeycloackClient = get_keycloak_service(oidc)

    yield

    logger.info("Закрываем соеденения.")
