from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Role(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
