import json
from functools import lru_cache
from typing import Any, Callable, Literal

import aiohttp
from core.settings import IDPSettings
from opentelemetry import trace

Verb = Literal["POST", "GET", "DELETE", "PUT", "PATCH"]

tracer = trace.get_tracer(__name__)


class IDPClientService:
    def __init__(self, settings: IDPSettings):
        self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)
        self._settings = settings

    async def info(self) -> Any:
        url = f"{self._settings.url}/api/v1/users/token"
        payload = {"login": "jonny4@example.com", "password": "sample-password123"}
        smth = await self._send("POST", url, data=payload)

        print(smth)

    async def introspect(self, token: str) -> bool:
        url = f"{self._settings.url}/api/v1/users/introspect"
        response = await self._send("POST", url, headers={"Authorization": f"Bearer {token}"})
        return bool(response.get("valid", False))

    @staticmethod
    def _get_func_by_verb(verb: Verb, session: aiohttp.ClientSession) -> Callable:
        match verb:
            case "GET":
                return session.get
            case "POST":
                return session.post
            case "DELETE":
                return session.delete
            case "PUT":
                return session.put
            case "PATCH":
                return session.patch

    async def _send(
        self, verb: Verb, url: str, json: Any | None = None, data: Any | None = None, headers: dict | None = None
    ) -> Any:
        with tracer.start_as_current_span("idp-request") as span:
            # TODO(agrebennikov): Это неправильно, тут нужен request_id, а не trace_id,
            # вообще непонятно как это должно быть
            trace_id = span.get_span_context().trace_id
            request_id_header = {"X-Request-Id": format(trace_id, "x")}
            headers = {**headers, **request_id_header} if headers else request_id_header

            async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
                func = IDPClientService._get_func_by_verb(verb, session)
                async with func(url, json=json, data=data) as response:
                    return await self._handle_failed_response(response)

    async def _handle_failed_response(self, response: aiohttp.ClientResponse) -> dict:
        raw = await response.text()
        if response.ok:
            # some api calls return empty response
            return dict(json.loads(raw)) if raw else {}

        raise ValueError(raw)


@lru_cache()
def get_idp_client_service() -> IDPClientService:
    settings = IDPSettings()
    return IDPClientService(settings)
