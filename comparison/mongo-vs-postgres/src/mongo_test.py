"""
Mongo load tests

Start with locust -f mongo_test.py
"""

import copy
import json
import random
import string
from time import perf_counter_ns

from locust import HttpUser, TaskSet, between, events, task
from pymongo import InsertOne, MongoClient
from pymongo.collection import Collection

# Mongo configuration
MONGO_HOST = "host.docker.internal"
MONGO_PORT = 27017


def generate_random_data(batch_size) -> list[dict]:
    return [
        {
            "key": random.randint(1, 10_000_000),
            "value": "".join(random.choices(string.ascii_letters + string.digits, k=10)),
        }
        for _ in range(batch_size)
    ]


class MongoTasks(TaskSet):
    _client: MongoClient
    _collection: Collection
    _batch_size = 10
    _request_type = "mongoDB"
    _inserted: list[int] | None = None

    def on_start(self):
        self._client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = self._client["locust-test-db"]
        self._collection = db["test-collection"]
        self._collection.drop()
        self._collection.create_index({"key": 1})

    def on_stop(self):
        self._collection.drop()

    @task
    def read_mongo(self):
        start_time = perf_counter_ns()
        err = None
        result = []
        try:
            inserted = self._inserted or []
            ids = random.choices(inserted, k=self._batch_size) if len(inserted) > self._batch_size else inserted
            results = [r for r in self._collection.find({"key": {"$in": ids}})]
            print(f"Mongo found {len(results)} of {self._batch_size} saved {len(inserted)}")
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
    def write_mongo(self):
        start_time = perf_counter_ns()
        err = None
        batch_size = self._batch_size
        data = generate_random_data(batch_size)
        try:
            self._collection.bulk_write([InsertOne(copy.deepcopy(row)) for row in data])
            self._inserted = (self._inserted or []) + [r["key"] for r in data]
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


class Mongo1Tasks(MongoTasks):
    _batch_size = 1
    _request_type = "Mongo:1"


class Mongo10Tasks(MongoTasks):
    _batch_size = 10
    _request_type = "Mongo:10"


class Mongo100Tasks(MongoTasks):
    _batch_size = 100
    _request_type = "Mongo:100"


class DatabaseUser(HttpUser):
    wait_time = between(1, 5)
    # tasks = [Mongo10Tasks]
    tasks = {Mongo1Tasks: 1, Mongo10Tasks: 1, Mongo100Tasks: 1}
