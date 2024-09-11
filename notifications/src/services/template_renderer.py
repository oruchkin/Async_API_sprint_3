from uuid import UUID

import jinja2
from fastapi import Depends
from src.services.idp_client import IDPClient, get_idp_client


class TemplateRenderer:
    def __init__(self, idp: IDPClient):
        self._idp = idp

    async def render(self, template: str, user_id: UUID) -> str:
        j_template = jinja2.Environment().from_string(template)
        user = await self._idp.get_user(user_id)
        data = {"username": user.email}
        return j_template.render(data)


def get_template_renderer(idp=Depends(get_idp_client)) -> TemplateRenderer:
    return TemplateRenderer(idp)
