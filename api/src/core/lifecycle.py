import logging.config
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from redis.asyncio import Redis
from src.core.settings import ElasticsearchSettings, RedisSettings
from src.db import elastic, redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для установления соединения с базами данных.
    Запускается при старте и закрывает соединения при завершении работы приложения.
    """
    elastic_settings = ElasticsearchSettings()
    elastic.es = AsyncElasticsearch(hosts=[elastic_settings.url])
    redis_settings = RedisSettings()
    redis.redis = Redis(host=redis_settings.host, port=redis_settings.port, decode_responses=True)

    yield

    logger.info("Закрываем соеденения.")
    await redis.redis.close()
    await elastic.es.close()
