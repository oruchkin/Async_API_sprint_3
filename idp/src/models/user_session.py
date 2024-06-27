from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserSessionModel(BaseModel):
    model_config = ConfigDict(strict=False)

    id: UUID
    username: str
    userId: UUID
    ipAddress: str
    start: int
    lastAccess: int
    rememberMe: bool
    clients: dict
    """
    What client was used for the login
    """

    transientUser: bool
