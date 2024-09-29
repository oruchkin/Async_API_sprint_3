from uuid import UUID

from pydantic import BaseModel, ConfigDict
from src.models.notification import NotificationChannel


class NotificationDistribution(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel: NotificationChannel

    users: list[UUID]
