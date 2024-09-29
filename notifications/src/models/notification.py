from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

NotificationChannel = Literal["email", "sms", "push"]


class Notification(BaseModel):
    """
    Notification model stored in the DB
    """

    id: str
    channel: NotificationChannel
    users: list[UUID]
    template_id: str | None
    subject: str
    body: str
    created_at: datetime

    next_send: datetime

    schedule: str | None
    "cron-style schedule"

    last_sent: datetime | None
    status: Literal["processing", "idle"]
