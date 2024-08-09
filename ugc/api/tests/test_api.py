from unittest.mock import AsyncMock, patch

import pytest

# ignore import errors as it's controlled by the pytest.ini
from api.app import app  # type: ignore
from services.kafka_client import KafkaClient  # type: ignore


@pytest.fixture()
def runtime():
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here
    yield app
    # clean up / reset resources here


@pytest.fixture()
def client(runtime):
    return runtime.test_client()


@pytest.fixture()
def runner(runtime):
    return runtime.test_cli_runner()


def test_post_empty_data(client):
    response = client.post("/event", json={})
    assert not response.json["success"]


def test_post_wrong_type(client):
    response = client.post("/event", json={"type": "unkown-type"})
    assert not response.json["success"]


def test_post_invalid_model(runtime):
    client = runtime.test_client()
    response = client.post("/event", json={"type": "movie_progress"})
    assert not response.json["success"]
    assert len(response.json["validation"])


@patch.object(KafkaClient, "post_movie_progress", new_callable=AsyncMock)
def test_post_succeed(mock_kafka_post, runtime):
    payload = {
        "type": "movie_progress",
        "user_id": "4518e644-1ff3-4003-a14e-99dfe3fdd7ab",
        "movie_id": "e9897504-9b73-40bb-a22e-815daf7a190d",
        "progress": 123,
    }
    client = runtime.test_client()
    response = client.post("/event", json=payload)
    assert response.json["success"]
    assert mock_kafka_post.call_count == 1
