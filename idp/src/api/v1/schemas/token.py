from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    """
    is to request resource on behalf of that user (OAuth2.0) == authorization, it can be w/o authentication
    """

    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    """Usually Bearer"""

    id_token: str
    """
    who is the user (OpenID Connect), it's for app which requested the token == authentication
    """

    scope: str
