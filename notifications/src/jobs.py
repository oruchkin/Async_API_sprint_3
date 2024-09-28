import asyncio
import datetime
import logging
from random import random
from typing import Annotated

from fastapi import Depends
from src.core.dependencies_utils import solve_and_run
from src.core.settings import NOTIFICATION_TIMEOUT_SEC
from src.fastapi_app import app
from src.services.notifications_service import (
    NotificationsService,
    get_notifications_service,
)
from src.services.queue_service import QueueService, get_queue

logger = logging.getLogger(__name__)


async def send_notifications(
    notifications: Annotated[NotificationsService, Depends(get_notifications_service)],
    queue: Annotated[QueueService, Depends(get_queue)],
):
    slice = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=NOTIFICATION_TIMEOUT_SEC)
    while notification := await notifications.get_next_for_processing(slice):
        print(f"Sent notification {notification.id}")
        await queue.publish_notification(notification)
        await notifications.confirm(notification)


async def start_cron():
    # desync workers (if multiple)
    await asyncio.sleep(random() * 60)
    while 1:
        logger.info("Do the cron job")
        await solve_and_run(send_notifications, "send_notifications", app)
        await asyncio.sleep(NOTIFICATION_TIMEOUT_SEC)
