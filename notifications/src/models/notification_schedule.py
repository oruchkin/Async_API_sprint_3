from datetime import datetime

from pydantic import BaseModel
from src.models.notification import NotificationChannel


class NotificationSchedule(BaseModel):
    channel: NotificationChannel
    next_send: datetime | None

    schedule: str | None
    "cron-style schedule"
