from api.v1.schemas.film import Film


class FilmDetailed(Film):
    file: str | None
