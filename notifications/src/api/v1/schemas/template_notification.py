from pydantic import BaseModel, ConfigDict
from src import models


class TemplateNotification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schedule: models.NotificationSchedule

    distribution: models.NotificationDistribution
