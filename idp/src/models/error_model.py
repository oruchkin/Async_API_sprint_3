from pydantic import BaseModel, ConfigDict


class ErrorModel(BaseModel):
    model_config = ConfigDict(strict=False)

    error: str
    error_description: str
