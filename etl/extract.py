from typing import Any, Dict, Generator, List

import psycopg2
from decorators import backoff
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import DictCursor
from settings import Settings

settings = Settings()


@backoff()
def psycopg2_connection() -> PgConnection:
    """Создает подключение к базе данных Postgres."""
    dsl = {
        "dbname": settings.postgres_dbname,
        "user": settings.postgres_user,
        "password": settings.postgres_password,
        "host": settings.postgres_host,
        "port": settings.postgres_port,
        "options": "-c search_path=content",
    }
    return psycopg2.connect(**dsl, cursor_factory=DictCursor)


def extract_movies_data(pg_conn, state, batch_size) -> Generator[List[Dict[str, Any]], None, None]:
    """Извлекает данные о фильмах из базы данных Postgres."""

    last_modified_date = state.get_state("last_modified_movies") or settings.initial_date

    # FIXME: Тут мы выбираем всю базу разом. Курсор должен быть Server side (просто удалить DictCursor)
    # и сам запрос очень сложный, лучше сделать 3-4 отдельных запроса
    with pg_conn.cursor() as cursor:
        query = """
            SELECT fw.id,
                   fw.title,
                   fw.description,
                   fw.rating,
                   fw.file,
                   array_agg(DISTINCT jsonb_build_object('id', g.id, 'name', g.name)) AS genres,
                   array_agg(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
                   FILTER (WHERE pfw.role = 'director') AS directors,
                   array_agg(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
                   FILTER (WHERE pfw.role = 'actor') AS actors,
                   array_agg(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
                   FILTER (WHERE pfw.role = 'writer') AS writers,
                   MAX(GREATEST(fw.modified, g.modified, p.modified)) AS last_modified
            FROM film_work fw
            LEFT JOIN genre_film_work gfw ON fw.id = gfw.film_work_id
            LEFT JOIN genre g ON gfw.genre_id = g.id
            LEFT JOIN person_film_work pfw ON fw.id = pfw.film_work_id
            LEFT JOIN person p ON pfw.person_id = p.id
            WHERE fw.modified > %s OR g.modified > %s OR p.modified > %s
            GROUP BY fw.id
            ORDER BY last_modified DESC;
        """
        cursor.execute(query, (last_modified_date, last_modified_date, last_modified_date))

        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch


def extract_genres_data(pg_conn, state, batch_size=100) -> Generator[List[Dict[str, Any]], None, None]:
    """Извлекает данные о жанрах из базы данных Postgres."""

    last_modified_date = state.get_state("last_modified_genres") or settings.initial_date
    query = """
        SELECT id, name, description, modified AS last_modified
        FROM genre
        WHERE modified > %s
        ORDER BY modified DESC;
    """
    with pg_conn.cursor() as cursor:
        cursor.execute(query, (last_modified_date,))
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch


def extract_persons_data(pg_conn, state, batch_size=100) -> Generator[List[Dict[str, Any]], None, None]:
    """Извлекает данные о персонах из базы данных Postgres."""

    last_modified_date = state.get_state("last_modified_persons") or settings.initial_date
    query = """
        SELECT id, full_name, modified AS last_modified
        FROM person
        WHERE modified > %s
        ORDER BY modified DESC;
    """
    with pg_conn.cursor() as cursor:
        cursor.execute(query, (last_modified_date,))
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
