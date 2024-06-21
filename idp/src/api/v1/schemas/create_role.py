from pydantic import BaseModel, ConfigDict


class CreateRole(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str = ""
