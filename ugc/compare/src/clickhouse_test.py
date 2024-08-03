"""
ClickHouse load tests

Start with locust -f clickhouse_test.py
"""

import json
import random
import string
from time import perf_counter_ns
from typing import cast

from clickhouse_driver import Client
from locust import HttpUser, TaskSet, between, events, task

# ClickHouse configuration
clickhouse_host = "host.docker.internal"
clickhouse_port = "YOUR_CLICKHOUSE_PORT"
clickhouse_user = "YOUR_CLICKHOUSE_USER"
clickhouse_password = "YOUR_CLICKHOUSE_PASSWORD"
clickhouse_database = "YOUR_CLICKHOUSE_DATABASE"

def generate_random_data(batch_size):
    return [
        (
            random.randint(1, 1000),
            "".join(random.choices(string.ascii_letters + string.digits, k=10)),
        )
        for _ in range(batch_size)
    ]


CLICKHOUSE_CLUSTER = "company_cluster"
CLICKHOUSE_DB = "locust_test"


class ClickHouseTasks(TaskSet):
    _client: Client
    _batch_size = 10
    _request_type = "ClickHouse"

    def on_start(self):
        self._client = Client(host=clickhouse_host)
        self._client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB}")
        self._client.execute(f"DROP TABLE IF EXISTS {CLICKHOUSE_DB}.test_data")
        self._client.execute(f"""
                             CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB}.test_data
                             (id Int64, value TEXT) Engine=MergeTree() ORDER BY id
                             """)

    def on_stop(self):
        self._client.execute(f"DROP TABLE IF EXISTS {CLICKHOUSE_DB}.test_data")

    @task
    def read_clickhouse(self):
        start_time = perf_counter_ns()
        err = None
        result = []
        try:
            batch_size = self._batch_size
            result = cast(list, self._client.execute(f"SELECT * FROM {CLICKHOUSE_DB}.test_data LIMIT {batch_size}"))
            print(f"Clickhouse selected {len(result)} of {batch_size}")
        except Exception as e:
            print(e)
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
    def write_clickhouse(self):
        start_time = perf_counter_ns()
        err = None
        batch_size = self._batch_size
        data = generate_random_data(batch_size)
        try:
            self._client.execute(f"INSERT INTO {CLICKHOUSE_DB}.test_data (id, value) VALUES", data)
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


class ClickHouse10Tasks(ClickHouseTasks):
    _batch_size = 10
    _request_type = "ClickHouse:10"


class ClickHouse100Tasks(ClickHouseTasks):
    _batch_size = 100
    _request_type = "ClickHouse:100"


class ClickHouse10000Tasks(ClickHouseTasks):
    _batch_size = 10_000
    _request_type = "ClickHouse:10_000"


class DatabaseUser(HttpUser):
    wait_time = between(1, 5)
    tasks = [ClickHouse10000Tasks]
    # tasks = {
    #     ClickHouse10Tasks: 1,
    #     ClickHouse100Tasks: 1,
    #     ClickHouse10000Tasks: 1
    # }

