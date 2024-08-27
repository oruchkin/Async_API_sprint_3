import logging
import random
import time
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any
from uuid import UUID, uuid4

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import InsertOne
from src.db.mogno import get_mongo
from src.models.film_bookmark import FilmBookmark
from src.models.film_review import FilmReview
from src.models.film_user_rating import FilmUserRating


class UserPrefService:
    def __init__(self, mongo: AsyncIOMotorClient):
        self._mongo = mongo
        self._logger = logging.getLogger(__name__)

    async def populate_ratings(self, films: list[UUID]) -> None:
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
                collection = await self._get_movie_ratings_collection()
                await collection.bulk_write(requests=batch, ordered=False)
                self._logger.info("Populated 10K in %.2f sec", time.perf_counter() - start_batch)
                batch = []
                start_batch = time.perf_counter()

        self._logger.info("Populated in %.2f sec", time.perf_counter() - start)

    async def count_films_rating(self, film_ids: list[UUID]) -> list[FilmUserRating]:
        """
        Compute average users' films rating and number of votes.
        """
        start = time.perf_counter()
        pipeline: list[dict[str, Any]] = [
            {"$match": {"movie_id": {"$in": [str(id) for id in film_ids]}}},
            {"$group": {"_id": "$movie_id", "count": {"$count": {}}, "rating": {"$avg": "$value"}}},
            {"$project": {"id": "$_id", "count": 1, "rating": 1}},
        ]
        collection = await self._get_movie_ratings_collection()
        values = await collection.aggregate(pipeline).to_list(length=len(film_ids) * 2)
        elapsed = time.perf_counter() - start
        self._logger.info("Films rating counted in %.2f sec", elapsed)
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
        collection = await self._get_movie_ratings_collection()
        found = await collection.find(find).to_list(length=None)
        return {UUID(e["movie_id"]): e["value"] for e in found}

    async def upsert_movie_rating(self, user_id: UUID, film_id: UUID, rating: int | None) -> int | None:
        collection = await self._get_movie_ratings_collection()
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

    async def create_movie_review(self, user_id: UUID, film_id: UUID, review: str) -> FilmReview:
        collection = await self._get_movie_reviews_collection()
        if await collection.find_one({"user_id": str(user_id), "movie_id": str(film_id)}):
            raise RuntimeError("Что написано пером, того не вырубишь топором")

        doc = {
            "_id": ObjectId(),
            "user_id": str(user_id),
            "movie_id": str(film_id),
            "review": review,
            "created_at": datetime.now(UTC),
        }
        await collection.insert_one(doc)
        return FilmReview(
            id=str(doc["_id"]),
            user_id=user_id,
            review=review,
            movie_id=film_id,
            created_at=doc["created_at"],
            likes=0,
            dislikes=0,
        )

    async def list_movie_revies(self, movie_id: UUID) -> list[FilmReview]:
        filter = {"movie_id": str(movie_id)}
        return await self._list_rated_reviews(filter)

    async def list_user_reviews(self, user_id: UUID) -> list[FilmReview]:
        filter = {"user_id": str(user_id)}
        return await self._list_rated_reviews(filter)

    async def _list_rated_reviews(self, filter: dict[str, Any]) -> list[FilmReview]:
        collection = await self._get_movie_reviews_collection()
        pipeline_subdocument = [
            {"$group": {"_id": "$like", "count": {"$count": {}}}},
            {
                "$project": {
                    "_id": 0,
                    "v": "$count",
                    "k": {"$cond": {"if": "$_id", "then": "likes", "else": "dislikes"}},
                }
            },
        ]
        pipeline: list[dict[str, Any]] = [
            {"$match": filter},
            {
                "$lookup": {
                    "from": "movie_review_reactions",
                    "localField": "_id",
                    "foreignField": "review_id",
                    "as": "reactions",
                    "pipeline": pipeline_subdocument,
                }
            },
            {
                "$project": {
                    "user_id": 1,
                    "movie_id": 1,
                    "review": 1,
                    "created_at": 1,
                    "reactions": {"$arrayToObject": "$reactions"},
                }
            },
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "user_id": 1,
                    "movie_id": 1,
                    "review": 1,
                    "created_at": 1,
                    "likes": {"$ifNull": ["$reactions.likes", 0]},
                    "dislikes": {"$ifNull": ["$reactions.dislikes", 0]},
                }
            },
            {"$sort": {"likes": -1, "dislikes": 1}},
        ]
        result = await collection.aggregate(pipeline).to_list(length=None)
        return [FilmReview.model_validate(r) for r in result]

    async def rate_movie_review(self, user_id: UUID, review_id: ObjectId, like: bool | None) -> None:
        collection = await self._get_movie_review_reactions_collection()
        review_filter = {"user_id": str(user_id), "review_id": review_id}
        if like is None:
            await collection.delete_one(review_filter)

        else:
            if existing := await collection.find_one(review_filter):
                await collection.update_one({"_id": existing["_id"]}, {"$set": {"like": like}})
            else:
                doc = {"_id": ObjectId(), "user_id": str(user_id), "review_id": review_id, "like": like}
                await collection.insert_one(doc)

    async def add_movie_bookmark(self, user_id: UUID, movie_id: UUID) -> str:
        collection = await self._get_user_bookmarks_collection()
        doc = {
            "_id": ObjectId(),
            "user_id": str(user_id),
            "movie_id": str(movie_id),
            "created_at": datetime.now(UTC),
        }
        await collection.insert_one(doc)
        return str(doc["_id"])

    async def delete_movie_bookmark(self, bookmark_id: ObjectId, user_id: UUID) -> None:
        collection = await self._get_user_bookmarks_collection()
        # user_id filter is required to be sure that user removes own bookmarks
        await collection.delete_one({"_id": bookmark_id, "user_id": user_id})

    async def list_user_bookmarks(self, user_id: UUID, movie_ids: list[UUID] | None = None) -> list[FilmBookmark]:
        collection = await self._get_user_bookmarks_collection()
        filter = (
            {"user_id": str(user_id), "movie_id": {"$in": [str(id) for id in movie_ids]}}
            if movie_ids
            else {"user_id": str(user_id)}
        )
        results = await collection.find(filter).to_list(length=None)
        return [FilmBookmark.model_validate({**e, **{"id": str(e["_id"])}}) for e in results]

    async def _get_movie_ratings_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("user_pref_db")
        collection = db.get_collection("movie_likes")
        await collection.create_index({"user_id": 1})
        await collection.create_index({"movie_id": 1})
        return collection

    async def _get_movie_reviews_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("user_pref_db")
        collection = db.get_collection("movie_reviews")
        await collection.create_index({"user_id": 1})
        await collection.create_index({"movie_id": 1})
        return collection

    async def _get_movie_review_reactions_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("user_pref_db")
        collection = db.get_collection("movie_review_reactions")
        await collection.create_index({"user_id": 1})
        await collection.create_index({"review_id": 1})
        return collection

    async def _get_user_bookmarks_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("user_pref_db")
        collection = db.get_collection("user_movie_bookmarks")
        await collection.create_index({"user_id": 1})
        await collection.create_index({"movie_id": 1})
        return collection


@lru_cache()
def get_user_pref_service(
    mongo: AsyncIOMotorClient = Depends(get_mongo),
) -> UserPrefService:
    return UserPrefService(mongo)
