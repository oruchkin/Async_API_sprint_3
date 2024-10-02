from typing import Annotated
from uuid import UUID

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src import models
from src.db.mongo import get_mongo


class NotificationsSentService:
    def __init__(self, mongo: AsyncIOMotorClient):
        self._mongo = mongo

    async def add(self, notification: models.NotificationSent) -> None:
        collection = await self._get_collection()
        document = NotificationsSentService._to_mongo_document(notification)
        await collection.insert_one(document)

    async def get(self, user_id: UUID, limit: int = 10) -> list[models.NotificationSent]:
        collection = await self._get_collection()
        cursor = collection.find({"user": str(user_id)}).sort("sent_at", -1).limit(limit)
        return [NotificationsSentService._from_mongo_document(e) async for e in cursor]

    async def _get_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("notifications")
        collection = db.get_collection("notifications_sent")
        await collection.create_index({"user": 1, "sent_at": -1})
        return collection

    @staticmethod
    def _to_mongo_document(e: models.NotificationSent) -> dict:
        document = {
            **e.model_dump(),
            "_id": ObjectId(e.id) if e.id else ObjectId(),
            "user": str(e.user),
        }
        return document

    @staticmethod
    def _from_mongo_document(e: dict) -> models.NotificationSent:
        model = models.NotificationSent.model_validate({**e, **{"id": str(e["_id"])}})
        return model


def get_notifications_sent_service(
    mongo: Annotated[AsyncIOMotorClient, Depends(get_mongo)],
) -> NotificationsSentService:
    return NotificationsSentService(mongo)
