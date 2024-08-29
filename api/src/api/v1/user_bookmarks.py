import logging
from typing import Annotated
from uuid import UUID

from src.core.auth import AuthorizationProvider, TokenData
from bson import ObjectId
from fastapi import APIRouter, Depends
from pydantic import AfterValidator
from src.services.user_pref import UserPrefService, get_user_pref_service

router = APIRouter()


logger = logging.getLogger(__name__)


def check_object_id(value: str) -> str:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return value


@router.post("/")
async def create_bookmark(
    film_id: UUID,
    user: TokenData = Depends(AuthorizationProvider()),
    userpref: UserPrefService = Depends(get_user_pref_service),
):
    return await userpref.add_movie_bookmark(user.user_id, film_id)


@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: Annotated[str, AfterValidator(check_object_id)],
    user: TokenData = Depends(AuthorizationProvider()),
    userpref: UserPrefService = Depends(get_user_pref_service),
):
    return await userpref.delete_movie_bookmark(ObjectId(bookmark_id), user.user_id)


@router.get("/")
async def list_user_bookmarks(
    user_id: UUID, userpref: UserPrefService = Depends(get_user_pref_service)
):
    return await userpref.list_user_bookmarks(user_id)
