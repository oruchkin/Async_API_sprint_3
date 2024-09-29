from pydantic import BaseModel

from .notification_sent import NotificationSent


class NotificationSentQueuePayload(BaseModel):
    message: NotificationSent
