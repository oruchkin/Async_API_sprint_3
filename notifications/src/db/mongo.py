from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from src.core.settings import MongoSettings

mongo_client: AsyncIOMotorClient | None = None


def get_mongo() -> AsyncIOMotorClient:
    global mongo_client
    if not mongo_client:
        settings = MongoSettings()
        # Set the Stable API version when creating a new client
        mongo_client = AsyncIOMotorClient(settings.connection, server_api=ServerApi("1"))

    return mongo_client
