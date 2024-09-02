from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TemplateDistribution(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: list[UUID]
