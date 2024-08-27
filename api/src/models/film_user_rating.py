from uuid import UUID

from src.models.uitls import BaseOrjsonModel


class FilmUserRating(BaseOrjsonModel):
    id: UUID
    rating: float
    count: int
