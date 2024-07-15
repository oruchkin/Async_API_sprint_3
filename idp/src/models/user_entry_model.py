from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserEntryModel(BaseModel):
    model_config = ConfigDict(strict=False)

    id: UUID
    username: str
    email: str | None = None
    emailVerified: bool
    createdTimestamp: int
    enabled: bool
    totp: bool
    disableableCredentialTypes: list
    requiredActions: list
    notBefore: int
    access: dict
