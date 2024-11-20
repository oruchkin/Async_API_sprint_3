from http import HTTPStatus
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import TypeAdapter
from src.api.v1.schemas.film import Film
from src.api.v1.schemas.film_detailed import FilmDetailed
from src.api.v1.schemas.pagination import PaginatedParams
from src.core.auth import TokenData, get_current_user
from src.core.prometheus_metrics import movies_watch_amount
from src.core.settings import DjangoSettings, FileapiSettings
from src.db.redis import get_cache
from src.services.cache.storage import ICache
from src.services.film import FilmService, get_film_service
from src.services.user_pref import UserPrefService, get_user_pref_service

router = APIRouter()


SORT_OPTION = Literal["imdb_rating", "-imdb_rating"]


@router.get(
    "/",
    response_model=list[Film],
    summary="Список всех фильмов",
    description="Возвращает полный список фильмов",
)
async def list_films(
    response: Response,
    pagination: PaginatedParams = Depends(),
    sort: SORT_OPTION = Query("imdb_rating", description="Sorting options"),
    genre: UUID | None = Query(None, description="Films by genre"),
    user: TokenData | None = Depends(get_current_user),
    user_id: UUID | None = Query(None, description="User id from the access token"),
    film_service: FilmService = Depends(get_film_service),
    user_pref: UserPrefService = Depends(get_user_pref_service),
    cache: ICache = Depends(get_cache),
) -> list[Film]:
    user_id = user.user_id if user else user_id
    key = f"films:{pagination.page_number}:{pagination.page_size}:{genre}:{sort}"
    adapter = TypeAdapter(list[Film])
    if cached := await cache.get(key):
        return adapter.validate_json(cached)

    sort_object: dict[str, int] | None = None
    if sort:
        sort_object = {}
        # Maybe sort will be an array in future
        for item in [sort]:
            if item[0] == "-":
                sort_object[item[1:]] = -1
            else:
                sort_object[item] = 1
    films = await film_service.get_all_films(pagination.page_number, pagination.page_size, genre, sort_object)
    mapped = [Film.model_validate(film) for film in films]
    await _populate_rating(mapped, user_pref, user_id)

    cached = adapter.dump_json(mapped)
    await cache.set(key, cached, 60 * 5)
    response.headers["Cache-Control"] = f"max-age={60 * 5}"
    return mapped


@router.get(
    "/search",
    response_model=list[Film],
    summary="Поиск по фильмам",
    description="Возвращает список фильмов по поисковому запросу",
)
async def search_films(
    response: Response,
    query: str = Query(min_length=3, description="Search query string"),
    user_id: UUID | None = Query(None, description="User id from the access token"),
    pagination: PaginatedParams = Depends(),
    film_service: FilmService = Depends(get_film_service),
    user_pref: UserPrefService = Depends(get_user_pref_service),
    cache: ICache = Depends(get_cache),
) -> list[Film]:
    key = f"films:{query}:{pagination.page_number}:{pagination.page_size}"
    adapter = TypeAdapter(list[Film])
    if cached := await cache.get(key):
        return adapter.validate_json(cached)

    films = await film_service.search_films(query, pagination.page_number, pagination.page_size)
    mapped = [Film.model_validate(film) for film in films]
    await _populate_rating(mapped, user_pref, user_id)

    cached = adapter.dump_json(mapped)
    await cache.set(key, cached, 60 * 5)
    response.headers["Cache-Control"] = f"max-age={60 * 5}"
    return mapped


@router.get(
    "/{film_id}",
    response_model=FilmDetailed,
    summary="Данные по конкретному фильму",
    description="Возвращает подробную информацию о фильме.",
)
async def film_details(
    film_id: UUID,
    user_id: UUID | None = Query(None, description="User id from the access token"),
    film_service: FilmService = Depends(get_film_service),
    user_pref: UserPrefService = Depends(get_user_pref_service),
) -> FilmDetailed:
    if film := await film_service.get_by_id(film_id):
        model = FilmDetailed.model_validate(film)
        await _populate_rating([model], user_pref, user_id)
        for genre in film.genres:
            movies_watch_amount.labels(type=genre.name).inc()

        if model.file:
            fileapi = FileapiSettings()
            django = DjangoSettings()
            model.file = (
                f"{fileapi.url}/api/v1/files/redirect_download?short_name={model.file}&bucket={django.s3_bucket}"
            )
        return model

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")


async def _populate_rating(films: list[Film], user_pref: UserPrefService, user_id: UUID | None) -> None:
    ids = [f.id for f in films]
    ratings = await user_pref.count_films_rating(ids)
    user_ratings = await user_pref.list_user_ratings(user_id, ids) if user_id else {}
    bookmarked = await user_pref.list_user_bookmarks(user_id, ids) if user_id else []
    ratings_map = {r.id: r for r in ratings}
    bookmarked_set = {bm.movie_id for bm in bookmarked}
    for film in films:
        if film_rating := ratings_map.get(film.id):
            film.user_rating = film_rating.rating
            film.user_count = film_rating.count
        if (ur := user_ratings.get(film.id)) is not None:
            film.my_rating = ur
        film.is_bookmarked = film.id in bookmarked_set
