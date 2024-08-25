from uuid import UUID

from src.models.uitls import BaseOrjsonModel


class PersonId(BaseOrjsonModel):
    id: UUID
    name: str


class FilmUserRating(BaseOrjsonModel):
    id: UUID
    rating: float
    count: int
