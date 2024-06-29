from pydantic import BaseModel, ConfigDict, Field


class RefreshToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    refresh_token: str = Field(description="Refresh token value obtained with the /token call")
