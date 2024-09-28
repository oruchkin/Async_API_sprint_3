from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationSent(BaseModel):
    id: str = ""
    notification_id: str
    user: UUID
    subject: str
    body: str
    sent_at: datetime
