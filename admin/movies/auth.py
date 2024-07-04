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
        base_url = settings.AUTH_API_LOGIN_URL
        payload = {"login": username, "password": password}
        with requests.Session() as session:
            token_url = f"{base_url}/users/token"
            token_response = session.post(token_url, data=payload)
            if token_response.status_code != http.HTTPStatus.OK:
                return None

            token = token_response.json()
            user_url = f"{base_url}/users/me"
            headers = {"Authorization": f"{token['token_type']} {token['access_token']}"}
            data_response = session.get(user_url, headers=headers)
            if data_response.status_code != http.HTTPStatus.OK:
                return None
            data = data_response.json()
            #
            # 'user_id' = '82582cce-9229-4c00-842d-291223c19d14'
            # 'username' = 'jonny4@example.com'
            # 'email' = 'jonny4@example.com'
            # 'email_verified' = False
            # 'roles' = ['admin', 'one-more-role']

            print(data)

        try:
            response = User.objects.get_or_create(
                id=data["user_id"],
            )
            user: UserModel = cast(UserModel, response[0])
            user.email = data.get("email")
            user.is_admin = Roles.ADMIN in data.get("role", [])
            user.is_active = True  # data.get("email_verified")
            user.save()
        except Exception:
            # PermissionDenied
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
