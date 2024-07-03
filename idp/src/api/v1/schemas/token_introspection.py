from pydantic import BaseModel, ConfigDict


class TokenIntrospection(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    valid: bool
