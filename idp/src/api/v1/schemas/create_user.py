from pydantic import BaseModel, ConfigDict


class CreateUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    password: str
    username: str | None = None
