from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.models.notification import NotificationChannel


class NotificationSchedule(BaseModel):
    users: list[UUID]
    channel: NotificationChannel
    next_send: datetime | None

    schedule: str | None
    "cron-style schedule"
