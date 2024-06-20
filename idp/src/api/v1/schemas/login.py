from pydantic import BaseModel, ConfigDict


class Login(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login: str
    password: str
