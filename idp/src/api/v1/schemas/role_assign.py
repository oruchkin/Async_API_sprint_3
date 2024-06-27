from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoleAssign(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: list[UUID]
