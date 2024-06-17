from pydantic import BaseModel, ConfigDict


class RefreshToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    refresh_token: str
