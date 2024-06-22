from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ipAddress: str
    start: int
    lastAccess: int
    clients: dict
