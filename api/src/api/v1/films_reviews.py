import logging
from typing import Annotated
from uuid import UUID

from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from pydantic import AfterValidator
from src.api.v1.schemas.film_review_request import FilmReviewRequest
from src.core.auth import AuthorizationProvider, TokenData
from src.services.user_pref import UserPrefService, get_user_pref_service

router = APIRouter()


logger = logging.getLogger(__name__)


def check_object_id(value: str) -> str:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return value


@router.post("/{film_id}")
async def sumbit_review(
    film_id: UUID,
    req: Annotated[FilmReviewRequest, Body()],
    user: TokenData = Depends(AuthorizationProvider()),
    userpref: UserPrefService = Depends(get_user_pref_service),
):
    # TODO: Send notification
    # notifications.send({ film_id, user_id, review_id })
    return await userpref.create_movie_review(user.user_id, film_id, req.review)


@router.get("/user")
async def get_user_reviews(
    user: TokenData = Depends(AuthorizationProvider()),
    userpref: UserPrefService = Depends(get_user_pref_service),
):
    return await userpref.list_user_reviews(user.user_id)


@router.get("/{film_id}")
async def list_reviews(
    film_id: UUID,
    userpref: UserPrefService = Depends(get_user_pref_service),
):
    return await userpref.list_movie_revies(film_id)


@router.patch("/{review_id}")
async def set_like(
    review_id: Annotated[str, AfterValidator(check_object_id)],
    user: TokenData = Depends(AuthorizationProvider()),
    like: Annotated[bool | None, Body(description="User reaction, if None value will be removed")] = None,
    userpref: UserPrefService = Depends(get_user_pref_service),
):
    await userpref.rate_movie_review(user.user_id, ObjectId(review_id), like)
