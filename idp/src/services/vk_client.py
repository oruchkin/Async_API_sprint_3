import base64
import hashlib
import json
import urllib.parse
from functools import lru_cache
from http import HTTPStatus
from secrets import randbelow, token_urlsafe
from typing import Any, Callable, Literal

import aiohttp
import models
import services.errors as errors
from core.settings import VKSettings
from db.redis import get_redis
from fastapi import Depends
from redis.asyncio import Redis

# https://datatracker.ietf.org/doc/html/rfc7636#section-4.1
CODE_LENGTH = (43, 128)

Verb = Literal["POST", "GET", "DELETE", "PUT", "PATCH"]


class VKClient:
    def __init__(self, settings: VKSettings, redis: Redis):
        self._settings = settings
        self._redis = redis
        self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)

    async def get_auth_url(self) -> str:
        if not self._settings.client_id:
            raise ValueError("VK Client ID is not set")

        state = token_urlsafe(16)
        key = f"vk:auth:{state}"
        (verifier, challenge) = self._get_code_pair()
        pipeline = self._redis.pipeline()
        pipeline.set(key, json.dumps({"verifier": verifier}))
        pipeline.expire(key, 300)
        result = await pipeline.execute()
        print(result)

        params = {
            "response_type": "code",
            "client_id": self._settings.client_id,
            "scope": "email vkid.personal_info",
            "redirect_uri": self._settings.redirect_uri,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "s256",
        }

        return f"https://id.vk.com/authorize?{urllib.parse.urlencode(params)}"

    async def exchange(self, state: str, code: str, device_id: str) -> models.VKTokenModel:
        key = f"vk:auth:{state}"
        raw = await self._redis.get(key)
        token = json.loads(raw)
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": token["verifier"],
            "client_id": self._settings.client_id,
            "device_id": device_id,
            "redirect_uri": self._settings.redirect_uri,  # "http://localhost/api/v1/auth/vk/endpoint",
            "state": token_urlsafe(16),
        }
        url = "https://id.vk.com/oauth2/auth"
        data = await self._send("POST", url, data=params)
        return models.VKTokenModel.model_validate(data)

    def _get_code_pair(self) -> tuple[str, str]:
        verifier_length = randbelow(CODE_LENGTH[1] - CODE_LENGTH[0]) + CODE_LENGTH[0]
        code_verifier = token_urlsafe(verifier_length)

        code_challenge_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_hash).decode("utf-8")
        code_challenge = code_challenge.replace("=", "")
        return code_verifier, str(code_challenge)

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

    async def _send(self, verb: Verb, url: str, json: Any | None = None, data: Any | None = None) -> Any:
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            func = VKClient._get_func_by_verb(verb, session)
            async with func(url, json=json, data=data) as response:
                return await self._handle_failed_response(response)

    async def _handle_failed_response(self, response: aiohttp.ClientResponse) -> dict:
        raw = await response.text()
        if response.ok:
            # some api calls return empty response
            return dict(json.loads(raw)) if raw else {}

        data = json.loads(raw)
        error = self._get_error_message(data)

        if response.status == HTTPStatus.UNAUTHORIZED:
            self._access_token = None
            self._access_token_issued = None
            raise errors.NotAuthorizedError(error)

        if response.status == HTTPStatus.NOT_FOUND:
            raise errors.NotFoundError(error)

        raise errors.ValidationError(error)

    def _get_error_message(self, data: dict) -> str:
        if "errorMessage" in data:
            return str(data["errorMessage"])

        if "error" in data:
            return str(data["error"])

        return "Failed"


@lru_cache()
def get_vk_client(redis=Depends(get_redis)) -> VKClient:
    # Maybe not the best way to construct the class
    settings = VKSettings()
    client = VKClient(settings, redis)
    return client
