import asyncio
import logging.config

# Init queue
import src.queue  # noqa
from dotenv import load_dotenv
from src.core.logger import LOGGING
from src.fastapi_app import app, start_fastapi
from src.jobs import start_cron
from src.websocket import start_websocket

load_dotenv()
logging.config.dictConfig(LOGGING)
logging.basicConfig(level=logging.INFO)


async def main():
    await asyncio.gather(
        start_fastapi(),
        start_cron(app),
        start_websocket(app),
    )


if __name__ == "__main__":
    asyncio.run(main())
