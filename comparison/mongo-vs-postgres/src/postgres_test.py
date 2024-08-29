"""
PostgreSQL load tests

Start with locust -f postgres_test.py
"""

import json
import random
import string
from time import perf_counter_ns

import psycopg
from locust import HttpUser, TaskSet, between, events, task

# PostgreSQL configuration
PG_DSN = "postgresql://pguser:password123@host.docker.internal:5432/locust-test-db"


def generate_random_data(batch_size) -> list[tuple]:
    return [
        (
            random.randint(1, 10_000_000),
            "".join(random.choices(string.ascii_letters + string.digits, k=10)),
        )
        for _ in range(batch_size)
    ]


class PostgresTasks(TaskSet):
    _client: psycopg.Connection
    _cursor: psycopg.Cursor
    _batch_size = 10
    _request_type = "PostgreSQL"
    _inserted: list[int] | None = None

    def on_start(self):
        self._client = psycopg.connect(PG_DSN)
        self._client.autocommit = True
        self._cursor = self._client.cursor()
        self._cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS test_table (
            key INT NOT NULL,
            value VARCHAR(255) NOT NULL,
            PRIMARY KEY (key)
        );
        """
        )

    def on_stop(self):
        self._cursor.execute("DROP TABLE IF EXISTS test_table")
        self._cursor.close()
        self._client.close()

    @task
    def read_db(self):
        start_time = perf_counter_ns()
        err = None
        result = []
        try:
            inserted = self._inserted or []
            ids = random.choices(inserted, k=self._batch_size) if len(inserted) > self._batch_size else inserted
            cur = self._cursor.execute("SELECT * FROM test_table WHERE key = ANY(%(keys)s)", {"keys": ids})
            results = cur.fetchall()
            print(f"Postgres found {len(results)} of {self._batch_size} saved {len(inserted)}")
        except Exception as e:
            print(e)
            err = e

        total = (perf_counter_ns() - start_time) / 1_000_000
        events.request.fire(
            request_type=self._request_type,
            name="read",
            response_time=total,
            response_length=len(result),
            exception=err,
        )

    @task
    def write_db(self):
        start_time = perf_counter_ns()
        err = None
        batch_size = self._batch_size
        data = generate_random_data(batch_size)
        try:
            self._cursor.executemany("INSERT INTO test_table (key, value) VALUES (%s,%s) ON CONFLICT DO NOTHING", data)
            self._inserted = (self._inserted or []) + [r[0] for r in data]
        except Exception as e:
            print(e)
            err = e

        total = (perf_counter_ns() - start_time) / 1_000_000
        events.request.fire(
            request_type=self._request_type,
            name="write",
            response_time=total,
            response_length=len(json.dumps(data)),
            exception=err,
        )


class Postgres1Tasks(PostgresTasks):
    _batch_size = 1
    _request_type = "Postgres:1"


class Postgres10Tasks(PostgresTasks):
    _batch_size = 10
    _request_type = "Postgres:10"


class Postgres100Tasks(PostgresTasks):
    _batch_size = 100
    _request_type = "Postgres:100"


class DatabaseUser(HttpUser):
    wait_time = between(1, 5)
    # tasks = [Postgres10Tasks]
    tasks = {Postgres1Tasks: 1, Postgres10Tasks: 1, Postgres100Tasks: 1}
