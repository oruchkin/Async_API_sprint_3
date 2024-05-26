import os
import sqlite3
from contextlib import contextmanager

import psycopg2
from dataclasse import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


@contextmanager
def sqlite_connect(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def pg_connect(dsl: dict):
    conn = psycopg2.connect(**dsl, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def get_mogrified_values(pg_cursor, data_obj: dict):
    """Получение списка mogrified значений для вставки в PostgreSQL."""
    mogrified_values = pg_cursor.mogrify(
        ",".join(["%s"] * len(data_obj)), tuple(data_obj.values())
    )
    return mogrified_values


def save_data_to_postgres(pg_conn, table_name: str, data: list, columns: list):
    """Загрузка данных в PostgreSQL."""
    with pg_conn.cursor() as pg_cursor:
        # Формирование строки значений сразу в нужном формате
        args_str = ",".join(
            pg_cursor.mogrify(
                f"({','.join(['%s'] * len(row))})", tuple(row.values())
            ).decode()
            for row in data
        )

        # Формирование и выполнение SQL-запроса
        pg_cursor.execute(
            f"INSERT INTO content.{table_name} ({', '.join(columns)}) "
            f"VALUES {args_str} "
            f"ON CONFLICT DO NOTHING;"
        )
    pg_conn.commit()


def map_columns(row, column_mapping):
    """Преобразование названий колонок из SQLite в PostgreSQL."""
    new_row = {}
    for column, value in row.items():
        new_column = column_mapping.get(column, column)
        new_row[new_column] = value
    return new_row


def load_from_sqlite(sqlite_conn, pg_conn, batch_size=1000):
    mapping = {"created_at": "created", "updated_at": "modified"}
    tables = [
        {
            "name": "film_work",
            "dataclass": FilmWork,
            "column_mapping": mapping,
        },
        {
            "name": "genre",
            "dataclass": Genre,
            "column_mapping": mapping
        },
        {
            "name": "genre_film_work",
            "dataclass": GenreFilmWork,
            "column_mapping": mapping,
        },
        {
            "name": "person",
            "dataclass": Person,
            "column_mapping": mapping},
        {
            "name": "person_film_work",
            "dataclass": PersonFilmWork,
            "column_mapping": mapping,
        },
    ]

    for table in tables:
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table['name']};")

        while True:
            rows = sqlite_cursor.fetchmany(batch_size)
            if not rows:
                break

            data = [map_columns(dict(row), table["column_mapping"]) for row in rows]
            columns = list(data[0].keys()) if data else []
            save_data_to_postgres(pg_conn, table["name"], data, columns)


def main():
    sqlite_db_path = "db.sqlite"
    dsl = {
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT"),
    }

    # dsl = {
    #     "dbname": 'movies_database',
    #     "user": 'app',
    #     "password": '123qwe',
    #     "host": 'prac_db_postgres',
    #     "port": '5432',
    # }

    with sqlite_connect(sqlite_db_path) as sqlite_conn, pg_connect(dsl) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)


if __name__ == "__main__":
    main()
