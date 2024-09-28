import datetime
import logging
from typing import Annotated, Any, Callable, Coroutine

from fastapi import Depends
from src.core.dependencies_utils import solve_and_run
from src.db.rabbitmq import default_queue, rabbit_router, sent_notifications_queue
from src.fastapi_app import app
from src.models import (
    Notification,
    NotificationSent,
    NotificationSentQueuePayload,
    QueuePayload,
)
from src.services.idp_client import IDPClient, get_idp_client
from src.services.notifications_sent_service import (
    NotificationsSentService,
    get_notifications_sent_service,
)
from src.services.queue_service import QueueService, get_queue
from src.services.sendgrid_mail_sender import (
    SendgridMailSender,
    get_sendgrid_mail_sender,
)
from src.services.smtp_mail_sender import SMTPMailSender, get_smtp_mail_sender
from src.services.template_renderer import TemplateRenderer, get_template_renderer

logger = logging.getLogger(__name__)

Sender = Callable[[Notification], Coroutine[None, Any, Any]]


async def get_notification_mail_sender(
    renderer: Annotated[TemplateRenderer, Depends(get_template_renderer)],
    idp: Annotated[IDPClient, Depends(get_idp_client)],
    smtp: Annotated[SMTPMailSender, Depends(get_smtp_mail_sender)],
    sendgrid: Annotated[SendgridMailSender, Depends(get_sendgrid_mail_sender)],
    queue: Annotated[QueueService, Depends(get_queue)],
) -> Sender:
    async def sender(message: Notification) -> None:
        for user_id in message.users:
            user = await idp.get_user(user_id)
            subject = await renderer.render(message.subject, user_id)
            body = await renderer.render(message.body, user_id)
            # We can use setting to switch between providers
            sendgrid.send(user.email, subject, body)
            # smtp.send([user.email], subject, body)
            sent = NotificationSent(
                notification_id=message.id,
                user=user_id,
                subject=subject,
                body=body,
                sent_at=datetime.datetime.now(datetime.UTC),
            )
            await queue.publish_sent_notification(sent)

    return sender


@rabbit_router.subscriber(queue=default_queue)
async def handle_rabbit_message(payload: QueuePayload):
    # Asynchronous handling of the message
    logger.info(f"Received message: {payload.message.id}")
    print(f"Received message: {payload.message.id}")
    if payload.message.channel == "email":
        send: Sender = await solve_and_run(get_notification_mail_sender, "mail_sender", app)
        await send(payload.message)
    else:
        print(f"Unsupported channel {payload.message.channel}")
    print("Message processed")


Saver = Callable[[NotificationSent], Coroutine[None, Any, Any]]


async def get_notifications_storage(
    service: Annotated[NotificationsSentService, Depends(get_notifications_sent_service)],
) -> Saver:
    async def saver(message: NotificationSent) -> None:
        await service.add(message)

    return saver


@rabbit_router.subscriber(queue=sent_notifications_queue)
async def handle_sent_notification_message(payload: NotificationSentQueuePayload):
    # Asynchronous handling of the message
    logger.info(f"Received message: {payload.message.id}")
    print(f"Received message: {payload.message.id}")
    save: Saver = await solve_and_run(get_notifications_storage, "mail_saver", app)
    await save(payload.message)
    print("Message processed")
