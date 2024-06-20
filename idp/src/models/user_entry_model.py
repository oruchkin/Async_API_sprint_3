from pydantic import BaseModel, ConfigDict


class UserEntryModel(BaseModel):
    model_config = ConfigDict(strict=False)

    id: str
    username: str
    email: str
    emailVerified: bool
    createdTimestamp: int
    enabled: bool
    totp: bool
    disableableCredentialTypes: list
    requiredActions: list
    notBefore: int
    access: dict
