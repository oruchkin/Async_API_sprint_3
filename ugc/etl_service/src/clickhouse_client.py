import logging

import backoff
from clickhouse_driver import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClickHouseClient:
    def __init__(self, clickhouse_server: str):
        self.client = Client(clickhouse_server)

    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    def insert_data(self, data: list):
        try:
            self.client.execute('INSERT INTO ugc.movies_progress (user_id, movie_id, progress) VALUES', data)
            logger.info(f"Successfully inserted {len(data)} records into ClickHouse.")
        except Exception as e:
            logger.error(f"Failed to insert data into ClickHouse: {e}")
