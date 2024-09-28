import asyncio
import datetime
import logging.config
import secrets
import string
from random import random
from typing import Annotated

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from src.api.v1 import events, notify, templates
from src.core.dependencies_utils import solve_and_run
from src.core.lifecycle import lifespan
from src.core.logger import LOGGING
from src.core.settings import NOTIFICATION_TIMEOUT_SEC
from src.core.tracer import configure_tracer
from src.db.rabbitmq import rabbit_router
from src.services.notifications_service import (
    NotificationsService,
    get_notifications_service,
)

load_dotenv()
logging.config.dictConfig(LOGGING)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    log_config=LOGGING,
    log_level=logging.DEBUG,
)


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    trace_id = trace.get_current_span().get_span_context().trace_id
    current_span = trace.get_current_span()
    if current_span.is_recording():
        current_span.set_attribute("http.request_id", request_id or "NA")
        response = await call_next(request)
        response.headers["X-Trace-Id"] = format(trace_id, "x")
        response.headers["X-Request-Id"] = request_id or "NA"
        return response
    else:
        logger.warning("Trace not capturing, check middleware sequence")
        return await call_next(request)


# middlewares are executed from the bottom to top
# enabled opentelemetry after we set Request-Id but before we are adding attributes
configure_tracer(app)


@app.middleware("http")
async def ensure_request_id_header(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        alphabet = string.ascii_letters + string.digits
        request_id = "".join(secrets.choice(alphabet) for i in range(16))
        headers = request.headers.mutablecopy()
        delattr(request, "_headers")
        headers["X-Request-Id"] = request_id
        request.scope["headers"] = headers.raw

    return await call_next(request)


app.include_router(rabbit_router)

app.include_router(notify.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])


async def send_notifications(notifications: Annotated[NotificationsService, get_notifications_service]):
    slice = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=NOTIFICATION_TIMEOUT_SEC)
    while notification := await notifications.get_next_for_processing(slice):
        print(f"Sent notification {notification.id}")
        await notifications.confirm(notification)


async def start_cron():
    # desync workers (if multiple)
    await asyncio.sleep(random() * 60)
    while 1:
        await asyncio.sleep(2)
        logger.info("Do the cron job")
        solve_and_run(send_notifications, "send_notifications", app)


async def start_fastapi():
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        start_fastapi(),
        start_cron(),
    )


if __name__ == "__main__":
    asyncio.run(main())
