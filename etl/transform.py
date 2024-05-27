from typing import Any, Dict, List


class Movie:
    """Класс для хранения данных фильма."""

    def __init__(
        self,
        movie_id: str,
        title: str,
        description: str,
        rating: float,
        file: str,
        genres: list,
        directors: list | None = None,
        actors: list | None = None,
        writers: list | None = None,
    ):
        self.id = movie_id
        self.title = title
        self.description = description
        self.imdb_rating = rating
        self.genres = genres
        self.file = file
        self.directors = directors if directors is not None else []
        self.actors = actors if actors is not None else []
        self.writers = writers if writers is not None else []
        self.directors_names = [director["name"] for director in self.directors]
        self.actors_names = [actor["name"] for actor in self.actors]
        self.writers_names = [writer["name"] for writer in self.writers]

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "imdb_rating": self.imdb_rating,
            "genres": self.genres,
            "directors": self.directors,
            "actors": self.actors,
            "writers": self.writers,
            "directors_names": self.directors_names,
            "actors_names": self.actors_names,
            "writers_names": self.writers_names,
        }


def transform_movies_data(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Преобразует данные фильмов в формат для загрузки в ElasticSearch."""
    movies = []
    for row in batch:
        movie = Movie(
            movie_id=row["id"],
            title=row["title"],
            description=row["description"],
            rating=row["rating"],
            file=row["file"],
            genres=row["genres"],
            directors=row["directors"],
            actors=row["actors"],
            writers=row["writers"],
        )
        movies.append(movie.to_dict())
    return movies


def transform_genre_data(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Преобразует данные жанров в формат для загрузки в ElasticSearch."""
    genres = []
    for row in batch:
        genre = {"id": row["id"], "name": row["name"], "description": row["description"]}
        genres.append(genre)
    return genres


def transform_person_data(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Преобразует данные персон в формат для загрузки в ElasticSearch."""
    persons = []
    for row in batch:
        person = {
            "id": row["id"],
            "full_name": row["full_name"],
        }
        persons.append(person)
    return persons
