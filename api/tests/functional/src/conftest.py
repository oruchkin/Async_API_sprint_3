# Setup fixtures

# `functional.` is because of file locations in the container

pytest_plugins = (
    "functional.fixtures.elasticsearch_fixtures",
    "functional.fixtures.http_fixtures",
    "functional.fixtures.redis_fixtures",
)
