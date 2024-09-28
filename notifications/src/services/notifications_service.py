from datetime import UTC, datetime, timedelta
from typing import Annotated, cast

from bson import ObjectId
from croniter import croniter
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.core.settings import NOTIFICATION_TIMEOUT_SEC
from src.db.mogno import get_mongo
from src.models.notification import Notification
from src.models.notification_schedule import NotificationSchedule
from src.services.templates_service import TemplatesService, get_templates_service


class NotificationsService:
    def __init__(self, mongo: AsyncIOMotorClient, templates: TemplatesService):
        self._mongo = mongo
        self._templates = templates

    async def create_from_template(self, template_id: str, schedule: NotificationSchedule) -> None:
        template = await self._templates.get(ObjectId(template_id))
        if not template:
            raise KeyError(f"Template {template_id} not found")

        now = datetime.now(UTC)
        next_send = (
            NotificationsService.get_next_schedule(schedule.schedule)
            if schedule.schedule
            else schedule.next_send or now
        )
        if schedule.schedule and next_send < now + timedelta(seconds=NOTIFICATION_TIMEOUT_SEC):
            raise ValueError(f"Recurrent schedule can't be less than {NOTIFICATION_TIMEOUT_SEC} seconds")

        notification = Notification(
            id=str(ObjectId()),
            channel=schedule.channel,
            users=schedule.users,
            template_id=str(template_id),
            subject=template.subject,
            body=template.body,
            created_at=datetime.now(UTC),
            next_send=next_send,
            schedule=schedule.schedule,
            last_sent=None,
            status="idle",
        )
        document = {**notification.model_dump(), "_id": ObjectId(notification.id)}
        collection = await self._get_collection()
        await collection.insert_one(document)

    async def get_next_for_processing(self, slice: datetime) -> Notification | None:
        collection = await self._get_collection()
        notification = await collection.find_one_and_update(
            {"next_send": {"$gte": slice}, "last_sent": {"$lte": slice}, "status": "idle"}, {"status": "processing"}
        )
        return Notification.model_validate(notification) if notification else None

    async def confirm(self, notification: Notification) -> None:
        collection = await self._get_collection()
        next_send = (
            NotificationsService.get_next_schedule(notification.schedule)
            if notification.schedule
            else notification.next_send
        )
        now = datetime.now(UTC)
        await collection.update_one(
            {"_id": ObjectId(notification.id)}, {"status": "idle", "next_send": next_send, "last_sent": now}
        )

    async def _get_collection(self) -> AsyncIOMotorCollection:
        db = self._mongo.get_database("notifications")
        collection = db.get_collection("notifications_schedule")
        await collection.create_index({"next_send": -1, "last_sent": -1})
        return collection

    @staticmethod
    def get_next_schedule(schedule: str) -> datetime:
        base = datetime.now(UTC)
        iter = croniter(schedule, base)
        return cast(datetime, iter.next())


def get_notifications_service(
    mongo: Annotated[AsyncIOMotorClient, get_mongo], templates: Annotated[TemplatesService, get_templates_service]
) -> NotificationsService:
    return NotificationsService(mongo, templates)
