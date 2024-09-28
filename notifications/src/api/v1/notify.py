import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from faststream.rabbit.fastapi import RabbitBroker
from src.db.rabbitmq import default_queue, get_rabbitmq_broker
from src.services.notifications_service import (
    NotificationsService,
    get_notifications_service,
)

from . import schemas

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/notify", summary="Отправляем нотификация", response_model=None)
async def do_notify(
    notification: Annotated[schemas.CreateNotification, Body()],
    rabbitmq: Annotated[RabbitBroker, Depends(get_rabbitmq_broker)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
) -> schemas.NotificationSummary:
    try:
        model = await service.create(
            notification.subject, notification.body, notification.distribution, notification.schedule
        )
        if model.last_sent:
            status = await rabbitmq.publish({"m": {"notification_id": model.id}}, queue=default_queue)
            logger.info(status)

        return schemas.NotificationSummary.model_validate(model)

    except RuntimeError as err:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=repr(err))


@router.post("/notify/{template_id}", summary="Отправляем нотификацию из шаблона", response_model=None)
async def notify_by_template(
    template_id: str,
    notification: Annotated[schemas.TemplateNotification, Body()],
    rabbitmq: Annotated[RabbitBroker, Depends(get_rabbitmq_broker)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
) -> schemas.NotificationSummary:
    try:
        model = await service.create_from_template(template_id, notification.distribution, notification.schedule)
        if model.last_sent:
            status = await rabbitmq.publish({"m": {"notification_id": model.id}}, queue=default_queue)
            logger.info(status)
        return schemas.NotificationSummary.model_validate(model)
    except RuntimeError as err:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=repr(err))
