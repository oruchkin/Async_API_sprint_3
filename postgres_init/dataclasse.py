import datetime
import uuid
from dataclasses import dataclass


@dataclass
class FilmWork:
    id: uuid.UUID
    title: str
    description: str
    creation_date: datetime.datetime
    file: str
    rating: float
    type: str
    created: datetime.datetime
    modified: datetime.datetime


@dataclass
class Genre:
    id: uuid.UUID
    name: str
    description: str
    created: datetime.datetime
    modified: datetime.datetime


@dataclass
class GenreFilmWork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created: datetime.datetime


@dataclass
class Person:
    id: uuid.UUID
    full_name: str
    created: datetime.datetime
    modified: datetime.datetime


@dataclass
class PersonFilmWork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created: datetime.datetime
