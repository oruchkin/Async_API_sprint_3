import os
import sqlite3
from contextlib import contextmanager

import psycopg2
from dataclasse import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork
from dotenv import load_dotenv
from psycopg2 import sql
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
    mogrified_values = pg_cursor.mogrify(",".join(["%s"] * len(data_obj)), tuple(data_obj.values()))
    return mogrified_values


def save_data_to_postgres(pg_conn, table_name: str, data: list, columns: list):
    """Загрузка данных в PostgreSQL."""
    with pg_conn.cursor() as pg_cursor:
        # Формирование строки значений сразу в нужном формате
        args_str = ",".join(
            pg_cursor.mogrify(f"({','.join(['%s'] * len(row))})", tuple(row.values())).decode() for row in data
        )

        # Формирование и выполнение SQL-запроса
        pg_cursor.execute(
            f"INSERT INTO content.{table_name} ({', '.join(columns)}) " f"VALUES {args_str} " f"ON CONFLICT DO NOTHING;"
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
    # from SQLite to Postgres column
    mapping = {"created_at": "created", "updated_at": "modified"}
    tables = [
        {
            "name": "film_work",
            "dataclass": FilmWork,
            "column_mapping": mapping,
        },
        {"name": "genre", "dataclass": Genre, "column_mapping": mapping},
        {
            "name": "genre_film_work",
            "dataclass": GenreFilmWork,
            "column_mapping": mapping,
        },
        {"name": "person", "dataclass": Person, "column_mapping": mapping},
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
            if table["name"] == "film_work":
                for row in data:
                    row["creation_date"] = row["created"]
                    row["certificate"] = ""
                    row["description"] = ""
                    row["rating"] = 0
                    row["file"] = row.pop("file_path", None)

            if table["name"] == "genre":
                for row in data:
                    row["description"] = ""

            columns = list(data[0].keys()) if data else []
            save_data_to_postgres(pg_conn, table["name"], data, columns)


def _ensure_db_exists(database_name: str, dsl: dict[str, str]) -> None:
    default_dsl = {**dsl, "dbname": "postgres"}
    with pg_connect(default_dsl) as pg_conn:
        pg_conn.autocommit = True
        with pg_conn.cursor() as pg_cursor:
            pg_cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [database_name])
            exists = pg_cursor.fetchone() is not None
            if not exists:
                pg_cursor.execute(f"CREATE DATABASE {database_name};")


def main():
    sqlite_db_path = "db.sqlite"
    dsl = {
        "dbname": os.environ["ADMIN_POSTGRES_DB"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "host": os.environ["POSTGRES_HOST"],
        "port": os.environ["POSTGRES_PORT"],
    }

    _ensure_db_exists(os.environ["ADMIN_POSTGRES_DB"], dsl)

    with sqlite_connect(sqlite_db_path) as sqlite_conn, pg_connect(dsl) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)


if __name__ == "__main__":
    main()
