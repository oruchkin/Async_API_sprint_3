from uuid import UUID

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str
    emailVerified: bool
    createdTimestamp: int
    enabled: bool
