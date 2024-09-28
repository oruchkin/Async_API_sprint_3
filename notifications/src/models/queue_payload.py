from pydantic import BaseModel

from .notification import Notification


class QueuePayload(BaseModel):
    message: Notification
