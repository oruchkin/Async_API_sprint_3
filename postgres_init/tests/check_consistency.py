import re
import sqlite3
import unittest

import psycopg2
from dateutil.parser import parse
from psycopg2.extras import DictCursor

COLUMN_MAPPING = {
    "created_at": "created",
    "updated_at": "modified",
}


def connect_to_sqlite(db_path="../db.sqlite") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def connect_to_postgresql() -> psycopg2.extensions.connection:
    dsl = {
        "dbname": "movies_database",
        "user": "app",
        "password": "123qwe",
        "host": "127.0.0.1",
        "port": 5432,
    }
    return psycopg2.connect(**dsl, cursor_factory=DictCursor)


def normalize_datetime(value):
    datetime_pattern = re.compile(r"\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}")
    if value is None or not isinstance(value, str):
        return value
    if datetime_pattern.match(value):
        return parse(value)
    return value


def compare_data(
    sqlite_cursor, pg_cursor, table_name: str, column_mapping: dict
) -> bool:
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    sqlite_data = [dict(row) for row in sqlite_cursor.fetchall()]

    pg_cursor.execute(f"SELECT * FROM content.{table_name}")
    pg_data = [dict(row) for row in pg_cursor.fetchall()]
    # print(sqlite_data)
    # print(pg_data)
    if len(sqlite_data) != len(pg_data):
        print(
            f"Row count mismatch: SQLite has {len(sqlite_data)} rows, PostgreSQL has {len(pg_data)} rows"
        )
        return False

    for sqlite_row, pg_row in zip(sqlite_data, pg_data):
        for sqlite_column, sqlite_value in sqlite_row.items():
            pg_column = column_mapping.get(sqlite_column, sqlite_column)
            pg_value = pg_row[pg_column]

            # Normalize datetime values before comparison
            sqlite_value = normalize_datetime(sqlite_value)
            pg_value = normalize_datetime(pg_value)

            if sqlite_value != pg_value:
                print(
                    f"Mismatch in column '{sqlite_column}': SQLite value '{sqlite_value}' != PostgreSQL value '{pg_value}'"
                )
                return False

    return True


def count_raw_in_table(
    table_name: str,
    sqlite_cursor: sqlite3.Connection,
    pg_cursor: psycopg2.extensions.cursor,
) -> dict:
    """Считаем сколько рядов в таблице"""
    sq_query = f"SELECT COUNT(*) FROM {table_name}"
    sqlite_cursor.execute(sq_query)
    sqlite_count = int(sqlite_cursor.fetchone()[0])

    pg_query = f"SELECT COUNT(*) FROM content.{table_name}"
    pg_cursor.execute(pg_query)
    pg_count = int(dict(pg_cursor.fetchone())["count"])
    return {"sqlite_count": sqlite_count, "pg_count": pg_count}


class DataIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.sqlite_conn = connect_to_sqlite()
        self.sqlite_cursor = self.sqlite_conn.cursor()
        self.pg_conn = connect_to_postgresql()
        self.pg_cursor = self.pg_conn.cursor()

    def tearDown(self):
        self.sqlite_conn.close()
        self.pg_conn.close()

    def table_integrity(self, table_name):
        """Проверка целостности данных в таблице."""
        data_is_consistent = compare_data(
            self.sqlite_cursor, self.pg_cursor, table_name, COLUMN_MAPPING
        )
        print(data_is_consistent)
        self.assertTrue(data_is_consistent, "Data inconsistency found")

    def test_film_work_count(self):
        """Проверяем кол-во на одинаковое кол-во фильмов в table film_work."""
        data = count_raw_in_table("film_work", self.sqlite_cursor, self.pg_cursor)
        self.assertEqual(data["sqlite_count"], data["pg_count"])

    def test_genre_count(self):
        """Проверяем кол-во на одинаковое кол-во фильмов в table genre."""
        data = count_raw_in_table("genre", self.sqlite_cursor, self.pg_cursor)
        self.assertEqual(data["sqlite_count"], data["pg_count"])

    def test_genre_film_work_count(self):
        """Проверяем кол-во на одинаковое кол-во фильмов в table genre_film_work."""
        data = count_raw_in_table("genre_film_work", self.sqlite_cursor, self.pg_cursor)
        self.assertEqual(data["sqlite_count"], data["pg_count"])

    def test_person_count(self):
        """Проверяем кол-во на одинаковое кол-во фильмов в table person."""
        data = count_raw_in_table("person", self.sqlite_cursor, self.pg_cursor)
        self.assertEqual(data["sqlite_count"], data["pg_count"])

    def test_person_film_work_count(self):
        """Проверяем кол-во на одинаковое кол-во фильмов в table person_film_work."""
        data = count_raw_in_table(
            "person_film_work", self.sqlite_cursor, self.pg_cursor
        )
        self.assertEqual(data["sqlite_count"], data["pg_count"])

    def test_film_work_integrity(self):
        self.table_integrity("film_work")

    def test_genre_integrity(self):
        self.table_integrity("genre")

    def test_person_integrity(self):
        self.table_integrity("person")

    def test_genre_film_work_integrity(self):
        self.table_integrity("genre_film_work")

    def test_person_film_work_integrity(self):
        self.table_integrity("person_film_work")


if __name__ == "__main__":
    unittest.main()
