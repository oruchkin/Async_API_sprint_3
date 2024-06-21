from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoleEntryModel(BaseModel):
    model_config = ConfigDict(strict=False)

    id: UUID
    name: str
    description: str
    composite: bool
    clientRole: bool
    containerId: str
