from pydantic import BaseModel, ConfigDict
from src import models


class CreateNotification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subject: str

    body: str

    schedule: models.NotificationSchedule

    distribution: models.NotificationDistribution
