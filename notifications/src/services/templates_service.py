from datetime import UTC, datetime

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.db.mogno import get_mongo
from src.models.template import Template


class TemplatesService:
    def __init__(self, mongo: AsyncIOMotorClient):
        self._mongo = mongo

    async def get(self, id: ObjectId) -> Template | None:
        collection = await self._get_templates_collection()
        results = await collection.find({"_id": id}).to_list(length=1)
        if len(results):
            return Template.model_validate({**results[0], **{"id": str(results[0]["_id"])}})

        return None

    async def add(self, subject: str, body: str) -> Template:
        collection = await self._get_templates_collection()
        doc = {
            "_id": ObjectId(),
            "subject": subject,
            "body": body,
            "created_at": datetime.now(UTC),
        }
        await collection.insert_one(doc)
        return Template.model_validate({**doc, **{"id": str(doc["_id"])}})

    async def delete(self, id: ObjectId) -> None:
        collection = await self._get_templates_collection()
        # user_id filter is required to be sure that user removes own bookmarks
        await collection.delete_one({"_id": id})

    async def list(self) -> list[Template]:
        collection = await self._get_templates_collection()
        results = await collection.find({}).to_list(length=None)
        return [Template.model_validate({**e, **{"id": str(e["_id"])}}) for e in results]

    async def _get_templates_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("notifications")
        collection = db.get_collection("templates")
        await collection.create_index({"created_at": -1})
        return collection


def get_templates_service(mongo=Depends(get_mongo)) -> TemplatesService:
    return TemplatesService(mongo)
