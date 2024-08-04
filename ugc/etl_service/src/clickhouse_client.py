from clickhouse_driver import Client

class ClickHouseClient:
    # def __init__(self, host='clickhouse'):
    def __init__(self, host='localhost'):
        self.client = Client(host)

    def insert_data(self, data):
        self.client.execute('INSERT INTO ugc.movies_progress (user_id, movie_id, progress) VALUES', [data])
