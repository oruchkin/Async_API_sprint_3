import logging
from typing import Annotated
from uuid import UUID

import websockets
from fastapi import Depends
from src.services.oidc_client import OIDCClient, get_oidc_service


class WebsocketsService:
    def __init__(self, oidc: OIDCClient) -> None:
        self._clients: dict[UUID, websockets.WebSocketServerProtocol] = {}
        self._logger = logging.getLogger(__name__)
        self._oidc = oidc

    async def _authenticate(self, websocket: websockets.WebSocketServerProtocol) -> UUID | None:
        await websocket.send("Connected")
        received = await websocket.recv()
        try:
            user_id_raw = received if isinstance(received, str) else str(received)
            # TODO: It must be authentication header
            # user = await verify_token(self._oidc, user_id_raw)
            user_id = UUID(user_id_raw)
            self._clients[user_id] = websocket
            return user_id
        except Exception as e:
            self._logger.error("Failed to authenticate: %s", e)
            await websocket.send("Failed to authenticate")
            return None

    async def notify(self, user_id: UUID, message: str) -> None:
        if user_id not in self._clients:
            self._logger.warning("User %s is not connected", user_id)
            return
        await self._clients[user_id].send(message)

    async def receive(self, websocket: websockets.WebSocketServerProtocol, path: str) -> None:
        user_id = await self._authenticate(websocket)
        if not user_id:
            await websocket.close()
            return

        while True:
            try:
                raw = await websocket.recv()
                self._logger.info("Received: %s", raw)
                # don't care about the message, just listen for close
            except websockets.exceptions.ConnectionClosedOK:
                await self._clients[user_id].close()
                self._clients.pop(user_id)
                return


_service_instance: WebsocketsService | None = None


def get_websocket_service(oidc: Annotated[OIDCClient, Depends(get_oidc_service)]) -> WebsocketsService:
    global _service_instance
    if not _service_instance:
        _service_instance = WebsocketsService(oidc)
    return _service_instance
