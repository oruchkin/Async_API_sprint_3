from pydantic import BaseModel, ConfigDict


class FilmReviewRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review: str
