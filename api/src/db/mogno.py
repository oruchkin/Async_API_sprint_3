import os

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

mongo_client: AsyncIOMotorClient | None = None


def get_mongo() -> AsyncIOMotorClient:
    global mongo_client
    if not mongo_client:
        uri = os.environ["MONGO_CONNECTION"]
        # Set the Stable API version when creating a new client
        mongo_client = AsyncIOMotorClient(uri, server_api=ServerApi("1"))

    return mongo_client
