import json
import logging
from http import HTTPMethod
from typing import Any, Callable
from uuid import UUID

import aiohttp
import grpc
import src.services.idp_grpc.user_info_pb2 as user_info_pb2
import src.services.idp_grpc.user_info_pb2_grpc as user_info_pb2_grpc
from opentelemetry import trace
from src.core.settings import IDPSettings

tracer = trace.get_tracer(__name__)


class IDPClient:
    def __init__(self, settings: IDPSettings) -> None:
        self._settings = settings
        self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)
        self._logger = logging.getLogger(__name__)

    async def get_user(self, id: UUID) -> user_info_pb2.Info:
        try:
            # that might not work because it's listening on ipv6
            return await self._get_user_grpc(id)
        except grpc.aio._call.AioRpcError:
            self._logger.exception("Failed to get user with grpc %s", id)
            url = f"{self._settings.url}/api/v1/users/{id}"
            response = await self._send(HTTPMethod.GET, url)
            self._logger.info("Succeed %s", json.dumps(response))
            return user_info_pb2.Info(id=str(id), email=response["email"])

    async def _get_user_grpc(self, id: UUID) -> user_info_pb2.Info:
        async with grpc.aio.insecure_channel(self._settings.grpc) as channel:
            stub = user_info_pb2_grpc.UserInfoStub(channel)
            request = user_info_pb2.GetUserRequest(id=str(id))
            response = await stub.GetUser(request)
            return response

    @staticmethod
    def _get_func_by_verb(verb: HTTPMethod, session: aiohttp.ClientSession) -> Callable:
        match verb:
            case HTTPMethod.GET:
                return session.get
            case HTTPMethod.POST:
                return session.post
            case HTTPMethod.DELETE:
                return session.delete
            case HTTPMethod.PUT:
                return session.put
            case HTTPMethod.PATCH:
                return session.patch

        raise ValueError(f"Unsupported verb {verb}")

    async def _send(
        self,
        verb: HTTPMethod,
        url: str,
        json: Any | None = None,
        data: Any | None = None,
        headers: dict | None = None,
    ) -> Any:
        with tracer.start_as_current_span("idp-request") as span:
            # TODO(agrebennikov): Это неправильно, тут нужен request_id, а не trace_id,
            # вообще непонятно как это должно быть
            trace_id = span.get_span_context().trace_id
            request_id_header = {"X-Request-Id": format(trace_id, "x")}
            headers = {**headers, **request_id_header} if headers else request_id_header

            async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
                func = IDPClient._get_func_by_verb(verb, session)
                async with func(url, json=json, data=data) as response:
                    return await self._handle_failed_response(response)

    async def _handle_failed_response(self, response: aiohttp.ClientResponse) -> dict:
        raw = await response.text()
        if response.ok:
            # some api calls return empty response
            return dict(json.loads(raw)) if raw else {}

        raise ValueError(raw)


def get_idp_client() -> IDPClient:
    settings = IDPSettings()
    return IDPClient(settings)
