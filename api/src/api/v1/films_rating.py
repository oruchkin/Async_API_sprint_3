import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends
from src.services.film import FilmService, get_film_service
from src.services.user_pref import UserPrefService, get_user_pref_service

router = APIRouter()


logger = logging.getLogger(__name__)


@router.post("/populate")
async def populate_like(
    userpref: UserPrefService = Depends(get_user_pref_service), films: FilmService = Depends(get_film_service)
):
    all_films: list[UUID] = []
    page = 1

    while len(all_films) < 10_000:
        found = await films.get_all_films(page, 1000, genre=None, sort=None)
        if not found:
            break
        all_films += [f.id for f in found]
        page += 1

    await userpref.populate_ratings(all_films)


@router.get("/me")
async def get_liked(
    user_id: UUID,
    userpref: UserPrefService = Depends(get_user_pref_service),
):
    return await userpref.list_user_ratings(user_id)


@router.patch("/{film_id}")
async def set_like(
    user_id: UUID,
    film_id: UUID,
    rating: Annotated[
        int | None, Body(description="User rating 0..10, if None value will be removed", ge=0, le=10)
    ] = None,
    userpref: UserPrefService = Depends(get_user_pref_service),
):
    return await userpref.upsert_movie_rating(user_id, film_id, rating)
