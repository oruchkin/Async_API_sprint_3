from pydantic import BaseModel, ConfigDict


class RoleEntryModel(BaseModel):
    model_config = ConfigDict(strict=False)

    id: str
    name: str
    description: str
    composite: bool
    clientRole: bool
    containerId: str
