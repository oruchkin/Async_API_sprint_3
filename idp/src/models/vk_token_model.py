from pydantic import BaseModel, ConfigDict


class VKTokenModel(BaseModel):
    model_config = ConfigDict(strict=False)

    access_token: str
    refresh_token: str
    id_token: str
    """
    In JWT format
    """

    token_type: str
    """Usually Bearer"""

    expires_in: int
    user_id: int
    state: str

    session_state: str | None = None
    scope: str
