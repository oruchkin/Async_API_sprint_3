"""
Vertica load tests

Start with locust -f vertica_test.py
"""

import json
import random
import string
from time import perf_counter_ns
from typing import Any, Sequence, cast

import vertica_python
from locust import HttpUser, TaskSet, between, events, task
from vertica_python import Connection

# Vertica configuration
vertica_host = "host.docker.internal"
vertica_port = "5433"
vertica_user = "dbadmin"
vertica_password = "vertica"


def generate_random_data(batch_size):
    return [
        (
            random.randint(1, 1000),
            "".join(random.choices(string.ascii_letters + string.digits, k=10)),
        )
        for _ in range(batch_size)
    ]


class VerticaTasks(TaskSet):
    _client: Connection
    _batch_size = 10
    _request_type = "Vertica"

    def on_start(self):
        self._client = vertica_python.connect(
            host=vertica_host,
            port=vertica_port,
            user=vertica_user,
            password=vertica_password,
            autocommit=True,
            use_prepared_statements=True
        )
        cursor = self._client.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_data (
            id INTEGER,
            value VARCHAR(11) NOT NULL
            );
        """)

    def on_stop(self):
        cursor = self._client.cursor()
        try:
            cursor.execute("DROP TABLE IF EXISTS test_data")
        except vertica_python.errors.MissingRelation:
            pass  # ignore error
        self._client.close()

    @task
    def read_vertica(self):
        start_time = perf_counter_ns()
        err = None
        result = []
        try:
            batch_size = self._batch_size
            cursor = self._client.cursor()
            cursor.execute(f"SELECT * FROM test_data LIMIT {batch_size}")
            result = cursor.fetchall()
            print(f"Vertica selected {len(result)} of {batch_size}")
        except Exception as e:
            err = e

        total = (perf_counter_ns() - start_time) / 1_000_000
        events.request.fire(
            request_type=self._request_type,
            name="read",
            response_time=total,
            response_length=len(result),
            exception=err
        )

    @task
    def write_vertica(self):
        start_time = perf_counter_ns()
        err = None
        batch_size = self._batch_size
        data = generate_random_data(batch_size)
        try:
            cursor = self._client.cursor()
            cursor.executemany("INSERT INTO test_data VALUES (?, ?)", cast(Sequence[tuple[Any]], data))
        except Exception as e:
            print(e)
            err = e

        total = (perf_counter_ns() - start_time) / 1_000_000
        events.request.fire(
            request_type=self._request_type,
            name="write",
            response_time=total,
            response_length=len(json.dumps(data)),
            exception=err
        )


class Vertica10Tasks(VerticaTasks):
    _batch_size = 10
    _request_type = "Vertica:10"


class Vertica100Tasks(VerticaTasks):
    _batch_size = 100
    _request_type = "Vertica:100"


class Vertica1000Tasks(VerticaTasks):
    _batch_size = 1000
    _request_type = "Vertica:1000"


class Vertica10000Tasks(VerticaTasks):
    _batch_size = 10_000
    _request_type = "Vertica:10K"


class DatabaseUser(HttpUser):
    wait_time = between(1, 5)
    tasks = [Vertica100Tasks]
    # tasks = {
    #     Vertica10Tasks: 1,
    #     Vertica100Tasks: 1,
    #     Vertica10000Tasks: 1
    # }
