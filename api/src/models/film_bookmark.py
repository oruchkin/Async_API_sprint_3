from datetime import datetime
from uuid import UUID

from src.models.uitls import BaseOrjsonModel


class FilmBookmark(BaseOrjsonModel):
    id: str
    user_id: UUID
    movie_id: UUID
    created_at: datetime
