import logging

from elastic_indexes.genres_index_body import genres_index_body
from elastic_indexes.movies_index_body import movies_index_body
from elastic_indexes.persons_index_body import persons_index_body
from elasticsearch import Elasticsearch
from settings import Settings


def initialize_elastic() -> None:
    """Создает индексы в elastic search, если они не существуют."""
    settings = Settings()
    es_client = Elasticsearch(settings.elastic_url)

    movies_index = settings.elastic_index_name_movies
    genres_index = settings.elastic_index_name_genres
    persons_index = settings.elastic_index_name_persons

    if not es_client.indices.exists(index=movies_index):
        logging.warning(f"создан индекс в elastic search: {movies_index}")
        es_client.indices.create(index=movies_index, body=movies_index_body)

    if not es_client.indices.exists(index=genres_index):
        logging.warning(f"создан индекс в elastic search: {genres_index}")
        es_client.indices.create(index=genres_index, body=genres_index_body)

    if not es_client.indices.exists(index=persons_index):
        logging.warning(f"создан индекс в elastic search: {persons_index}")
        es_client.indices.create(index=persons_index, body=persons_index_body)
