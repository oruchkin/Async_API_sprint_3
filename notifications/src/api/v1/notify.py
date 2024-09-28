import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from src.services.notifications_service import (
    NotificationsService,
    get_notifications_service,
)
from src.services.queue_service import QueueService, get_queue

from . import schemas

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/notify", summary="Отправляем нотификация", response_model=None)
async def do_notify(
    notification: Annotated[schemas.CreateNotification, Body()],
    queue: Annotated[QueueService, Depends(get_queue)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
) -> schemas.NotificationSummary:
    try:
        model = await service.create(
            notification.subject, notification.body, notification.distribution, notification.schedule
        )
        if model.last_sent:
            await queue.publish_notification(model)

        return schemas.NotificationSummary.model_validate(model)

    except RuntimeError as err:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=repr(err))


@router.post("/notify/{template_id}", summary="Отправляем нотификацию из шаблона", response_model=None)
async def notify_by_template(
    template_id: str,
    notification: Annotated[schemas.TemplateNotification, Body()],
    queue: Annotated[QueueService, Depends(get_queue)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
) -> schemas.NotificationSummary:
    try:
        model = await service.create_from_template(template_id, notification.distribution, notification.schedule)
        if model.last_sent:
            await queue.publish_notification(model)
        return schemas.NotificationSummary.model_validate(model)
    except RuntimeError as err:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=repr(err))
