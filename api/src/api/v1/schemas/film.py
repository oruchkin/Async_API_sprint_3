from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Film(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    imdb_rating: float
    user_rating: float = 0
    user_count: int = 0
    my_rating: int | None = None
    is_bookmarked: bool = False
