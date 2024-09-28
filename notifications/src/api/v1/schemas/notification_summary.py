from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str

    next_send: datetime
