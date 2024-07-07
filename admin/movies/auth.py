import http
from enum import StrEnum
from typing import cast

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from .models import User as UserModel

User = get_user_model()


class Roles(StrEnum):
    ADMIN = "admin"


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        if not username or not password:
            return None

        data = self._login(username, password)
        if not data:
            return None

        try:
            response = User.objects.get_or_create(
                id=data["user_id"],
            )
            user: UserModel = cast(UserModel, response[0])
            user.email = data["email"]
            user.is_admin = True  # Roles.ADMIN in data.get("role", [])
            user.is_active = True  # data.get("email_verified")
            user.is_staff = True
            user.set_unusable_password()
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _login(self, username: str, password: str) -> dict | None:
        base_url = settings.AUTH_API_LOGIN_URL
        payload = {"login": username, "password": password}
        with requests.Session() as session:
            url = f"{base_url}/users/login"
            response = session.post(url, data=payload)
            if response.status_code != http.HTTPStatus.OK:
                return None

            return response.json()
