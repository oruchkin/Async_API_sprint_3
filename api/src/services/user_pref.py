import logging
import random
import time
from functools import lru_cache
from typing import Any
from uuid import UUID, uuid4

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import InsertOne
from src.db.mogno import get_mongo
from src.models.film_user_rating import FilmUserRating


class UserPrefService:
    def __init__(self, mongo: AsyncIOMotorClient):
        self._mongo = mongo
        self._logger = logging.getLogger(__name__)

    async def populate_likes(self, films: list[UUID]) -> None:
        """
        For dev purpose only.
        Populate database if movies reactions.
        """
        start = time.perf_counter()
        users = [str(uuid4()) for _ in range(10_000)]

        batch = []
        start_batch = time.perf_counter()

        for user in users:
            rated_films = random.choices(films, k=100)
            batch += [
                InsertOne({"movie_id": str(f), "user_id": user, "value": random.randint(0, 10)}) for f in rated_films
            ]

            if len(batch) >= 10_000:
                collection = await self._get_movie_likes_collection()
                await collection.bulk_write(requests=batch, ordered=False)
                self._logger.info("Populated 10K in %.2f sec", time.perf_counter() - start_batch)
                batch = []
                start_batch = time.perf_counter()

        self._logger.info("Populated in %.2f sec", time.perf_counter() - start)

    async def count_films_rating(self, film_ids: list[UUID]) -> list[FilmUserRating]:
        """
        Compute average users' films rating and number of votes.
        """
        pipeline: list[dict[str, Any]] = [
            {"$match": {"movie_id": {"$in": [str(id) for id in film_ids]}}},
            {"$group": {"_id": "$movie_id", "count": {"$count": {}}, "rating": {"$avg": "$value"}}},
            {"$project": {"id": "$_id", "count": 1, "rating": 1}},
        ]
        collection = await self._get_movie_likes_collection()
        values = await collection.aggregate(pipeline).to_list(length=len(film_ids) * 2)
        return [FilmUserRating.model_validate(v) for v in values]

    async def list_user_ratings(self, user_id: UUID, films: list[UUID] | None = None) -> dict[UUID, int]:
        """
        Get all ratings left by the user.
        """
        find: dict[str, Any] = (
            {"user_id": str(user_id)}
            if films is None
            else {"user_id": str(user_id), "movie_id": {"$in": [str(id) for id in films]}}
        )
        collection = await self._get_movie_likes_collection()
        found = await collection.find(find).to_list(length=None)
        return {UUID(e["movie_id"]): e["value"] for e in found}

    async def upsert_movie_rating(self, user_id: UUID, film_id: UUID, rating: int | None) -> int | None:
        collection = await self._get_movie_likes_collection()
        row_filter = {"user_id": str(user_id), "movie_id": str(film_id)}
        if rating is None:
            await collection.delete_one(row_filter)
        else:
            if existing := await collection.find_one(row_filter):
                await collection.update_one({"_id": existing["_id"]}, {"$set": {"value": rating}})
            else:
                doc = {"_id": ObjectId(), "user_id": str(user_id), "movie_id": str(film_id), "value": rating}
                await collection.insert_one(doc)

        return rating

    async def _get_movie_likes_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("user_pref_db")
        collection = db.get_collection("movie_likes")
        await collection.create_index({"user_id": 1})
        await collection.create_index({"movie_id": 1})
        return collection


@lru_cache()
def get_user_pref_service(
    mongo: AsyncIOMotorClient = Depends(get_mongo),
) -> UserPrefService:
    return UserPrefService(mongo)
