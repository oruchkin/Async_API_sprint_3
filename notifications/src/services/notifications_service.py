from datetime import UTC, datetime, timedelta
from typing import Annotated

from bson import ObjectId
from croniter import croniter
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src import models
from src.core.settings import NOTIFICATION_TIMEOUT_SEC
from src.services.templates_service import TemplatesService, get_templates_service

from notifications.src.db.mongo import get_mongo


class NotificationsService:
    def __init__(self, mongo: AsyncIOMotorClient, templates: TemplatesService):
        self._mongo = mongo
        self._templates = templates

    async def create(
        self,
        subject: str,
        body: str,
        distribution: models.NotificationDistribution,
        schedule: models.NotificationSchedule,
    ) -> models.Notification:
        now = datetime.now(UTC)
        next_send = NotificationsService.get_next_schedule_validated(schedule)
        notification = models.Notification(
            id=str(ObjectId()),
            channel=schedule.channel,
            users=distribution.users,
            template_id=None,
            subject=subject,
            body=body,
            created_at=datetime.now(UTC),
            next_send=next_send or now,
            schedule=schedule.schedule,
            last_sent=None if next_send else now,
            status="idle",
        )
        document = NotificationsService._to_mongo_document(notification)
        collection = await self._get_collection()
        await collection.insert_one(document)
        return notification

    async def create_from_template(
        self, template_id: str, distribution: models.NotificationDistribution, schedule: models.NotificationSchedule
    ) -> models.Notification:
        template = await self._templates.get(ObjectId(template_id))
        if not template:
            raise KeyError(f"Template {template_id} not found")

        next_send = NotificationsService.get_next_schedule_validated(schedule)
        now = datetime.now(UTC)
        notification = models.Notification(
            id=str(ObjectId()),
            channel=schedule.channel,
            users=distribution.users,
            template_id=str(template_id),
            subject=template.subject,
            body=template.body,
            created_at=datetime.now(UTC),
            next_send=next_send or now,
            schedule=schedule.schedule,
            last_sent=None if next_send else now,
            status="idle",
        )
        document = NotificationsService._to_mongo_document(notification)
        collection = await self._get_collection()
        await collection.insert_one(document)
        return notification

    async def get_next_for_processing(self) -> models.Notification | None:
        collection = await self._get_collection()
        now = datetime.now(UTC)
        found = await collection.find_one_and_update(
            {"next_send": {"$lte": now}, "last_sent": {"$not": {"$gt": "$next_send"}}, "status": "idle"},
            {"$set": {"status": "processing"}},
        )
        return NotificationsService._from_mongo_document(found) if found else None

    async def confirm(self, notification: models.Notification) -> None:
        collection = await self._get_collection()
        next_send = (
            NotificationsService.get_next_schedule(notification.schedule)
            if notification.schedule
            else notification.next_send
        )
        now = datetime.now(UTC)
        await collection.update_one(
            {"_id": ObjectId(notification.id)}, {"$set": {"status": "idle", "next_send": next_send, "last_sent": now}}
        )

    async def _get_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("notifications")
        collection = db.get_collection("notifications_schedule")
        await collection.create_index({"next_send": -1, "last_sent": -1})
        return collection

    @staticmethod
    def get_next_schedule_validated(schedule: models.NotificationSchedule) -> datetime | None:
        if schedule.schedule:
            now = datetime.now(UTC)
            next = NotificationsService.get_next_schedule(schedule.schedule)
            if next < now + timedelta(seconds=NOTIFICATION_TIMEOUT_SEC):
                raise RuntimeError(f"Recurrent schedule can't be less than {NOTIFICATION_TIMEOUT_SEC} seconds")

            return next

        return schedule.next_send

    @staticmethod
    def get_next_schedule(schedule: str) -> datetime:
        base = datetime.now(UTC)
        iter = croniter(schedule, base)
        next: datetime = iter.next(datetime)
        return next

    @staticmethod
    def _to_mongo_document(e: models.Notification) -> dict:
        document = {
            **e.model_dump(),
            "_id": ObjectId(e.id),
            "users": [str(id) for id in e.users],
        }
        return document

    @staticmethod
    def _from_mongo_document(e: dict) -> models.Notification:
        model = models.Notification.model_validate({**e, **{"id": str(e["_id"])}})
        return model


def get_notifications_service(
    mongo: Annotated[AsyncIOMotorClient, Depends(get_mongo)],
    templates: Annotated[TemplatesService, Depends(get_templates_service)],
) -> NotificationsService:
    return NotificationsService(mongo, templates)
