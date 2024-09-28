import asyncio
import logging.config

import src.queue  # noqa
from dotenv import load_dotenv
from src.core.logger import LOGGING
from src.fastapi_app import start_fastapi
from src.jobs import start_cron

load_dotenv()
logging.config.dictConfig(LOGGING)
logging.basicConfig(level=logging.INFO)


async def main():
    await asyncio.gather(
        start_fastapi(),
        start_cron(),
    )


if __name__ == "__main__":
    asyncio.run(main())
