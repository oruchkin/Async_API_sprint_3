import logging
import time

from elasticsearch import Elasticsearch

from extract import extract_movies_data, extract_genres_data, extract_persons_data, psycopg2_connection
from init_elastic_search_index import initialize_elastic
from load import upload_to_elastic
from settings import Settings
from state_storage import JsonFileStorage, State
from transform import transform_movies_data, transform_genre_data, transform_person_data

settings = Settings()
state_storage = JsonFileStorage(settings.state_file_path)
state = State(state_storage)
initialize_elastic()


def run_etl_for_table(extract_func, transform_func, index_name):
    """ Выполняет ETL процесс для входящей таблицы и индекса. """

    pg_conn = psycopg2_connection()
    es_client = Elasticsearch([{'host': settings.elastic_host,
                                'port': settings.elastic_port,
                                'scheme': settings.elastic_schema}])

    for batch in extract_func(pg_conn, state, batch_size=300):
        if batch:
            last_record = batch[-1]
            last_modified = last_record['last_modified'] \
                                .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            transformed_batch = transform_func(batch)
            if transformed_batch:
                upload_to_elastic(transformed_batch, es_client, index_name)
            state.set_state(f'last_modified_{index_name}', last_modified)
            logging.warning(f"Uploaded {len(transformed_batch)} records to index: '{index_name}'")


def main():
    while True:
        run_etl_for_table(extract_genres_data, transform_genre_data, 'genres')
        run_etl_for_table(extract_persons_data, transform_person_data, 'persons')
        run_etl_for_table(extract_movies_data, transform_movies_data, 'movies')
        time.sleep(settings.delay)


if __name__ == '__main__':
    main()
