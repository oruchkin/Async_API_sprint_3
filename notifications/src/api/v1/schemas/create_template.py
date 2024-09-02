from pydantic import BaseModel, ConfigDict


class CreateTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subject: str
    body: str
