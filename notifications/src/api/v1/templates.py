from http import HTTPStatus
from typing import Annotated, Any

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import AfterValidator
from src.api.v1.schemas.create_template import CreateTemplate
from src.services.idp_client import IDPClient, get_idp_client
from src.services.smtp_mail_sender import SMTPMailSender, get_smtp_mail_sender
from src.services.template_renderer import TemplateRenderer, get_template_renderer
from src.services.templates_service import TemplatesService, get_templates_service

router = APIRouter()


def check_object_id(value: str) -> str:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return value


@router.get("/", summary="List all templates")
async def list_templates(templates: TemplatesService = Depends(get_templates_service)) -> list:
    all = await templates.list()
    return [t.model_dump() for t in all]


@router.post("/", summary="Create template")
async def create_template(req: CreateTemplate, templates: TemplatesService = Depends(get_templates_service)) -> Any:
    created = await templates.add(req.subject, req.body)
    return created.model_dump()


@router.delete("/{id}", summary="Deletes template")
async def delete_template(
    id: Annotated[str, AfterValidator(check_object_id)], templates: TemplatesService = Depends(get_templates_service)
):
    await templates.delete(ObjectId(id))


# @router.post("/{id}/send", summary="Send message based on the template")
# async def send_template(
#     id: Annotated[str, AfterValidator(check_object_id)],
#     distribution: TemplateDistribution,
#     templates: TemplatesService = Depends(get_templates_service),
#     renderer: TemplateRenderer = Depends(get_template_renderer),
#     idp: IDPClient = Depends(get_idp_client),
#     smtp: SMTPMailSender = Depends(get_smtp_mail_sender),
# ) -> None:
#     template = await templates.get(ObjectId(id))
#     if not template:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Template not found")

#     for user_id in distribution.users:
#         user = await idp.get_user(user_id)
#         subject = await renderer.render(template.subject, user_id)
#         body = await renderer.render(template.body, user_id)
#         # TODO: Do not send, push into the queue
#         smtp.send([user.email], subject, body)
