from pydantic import BaseModel, ConfigDict


class RoleModify(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str
