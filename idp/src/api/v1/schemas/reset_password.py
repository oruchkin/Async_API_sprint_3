from pydantic import BaseModel, ConfigDict


class ResetPassword(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    password: str
