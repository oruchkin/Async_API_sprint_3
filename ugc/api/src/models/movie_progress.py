from uuid import UUID

from pydantic import BaseModel


class MovieProgress(BaseModel):
    user_id: UUID
    movie_id: UUID
    progress: int
