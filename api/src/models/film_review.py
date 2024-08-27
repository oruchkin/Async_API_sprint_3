from datetime import datetime
from uuid import UUID

from src.models.uitls import BaseOrjsonModel


class FilmReview(BaseOrjsonModel):
    id: str
    review: str
    user_id: UUID
    movie_id: UUID
    created_at: datetime
    likes: int
    dislikes: int
