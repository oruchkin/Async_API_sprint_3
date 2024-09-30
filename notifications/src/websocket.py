import asyncio
import logging

import websockets
from fastapi import FastAPI
from src.core.dependencies_utils import solve_and_run
from src.services.websockets_service import WebsocketsService, get_websocket_service

logger = logging.getLogger(__name__)


async def start_websocket(app: FastAPI) -> None:
    service: WebsocketsService = await solve_and_run(get_websocket_service, "get_websocket_service", app)

    async def receiver(websocket, path):
        await service.receive(websocket, path)

    logger.info("Starting websocket server")
    async with websockets.serve(receiver, "localhost", 8765):
        await asyncio.Future()
        logger.info("Websocket server stopped")
