from uuid import UUID

from src.models.uitls import BaseOrjsonModel


class Person(BaseOrjsonModel):
    id: UUID
    full_name: str
