import time
import warnings

from loguru import logger
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchWarning

from db.session import db_session
from db.db import connect_to_db
from loaders.es_loader import ElasticsearchLoader
from loaders.postgres_loader import PostgresLoader
from utils.data_states import state
from core.config import settings

class EtlLoader:
    def __init__(self, es):
        self.es = es

    def load_movies_index(self, pg_loader, etl_loader):
        film_works = pg_loader.get_film_works_all()

        for film_work in film_works:
            all_genres = pg_loader.get_genres_by_fw_id(film_work.id)
            film_work.genres = [genre.name for genre in all_genres]

            all_persons = pg_loader.get_persons_by_fw_id(film_work.id)
            film_work.persons = [person.dict() for person in all_persons]

            film_work.actors_names = [
                person.full_name for person in all_persons
                if person.role == 'actor'
            ]

            film_work.writers_names = [
                person.full_name for person in all_persons
                if person.role == 'writer'
            ]

            film_work.director = [
                person.full_name for person in all_persons
                if person.role == 'director'
            ]

            film_work.actors = [
                {
                    "id": person.id,
                    "name": person.full_name
                } for person in all_persons
                if person.role == 'actor'
            ]

            film_work.writers = [
                {
                    "id": person.id,
                    "name": person.full_name
                } for person in all_persons
                if person.role == 'writer'
            ]

        etl_loader.bulk_load_film_works(film_works=film_works)
        logger.info(f"Загрузка индекса movies - успешно загружено {len(film_works)} фильмов")

    def load_persons_index(self, pg_loader, etl_loader):
        persons = pg_loader.get_persons_all()
        logger.info("persons are loading")

        for person in persons:
            all_film_works = pg_loader.get_film_works_by_p_id(person.id)
            person.films = [
                {
                    "id": film_work.id,
                    "title": film_work.title,
                    "roles": film_work.role
                } for film_work in all_film_works
            ]

        etl_loader.bulk_load_persons(persons=persons)
        logger.info(f"Загрузка индекса persons - успешно загружено {len(persons)} персон")

    def load_genres_index(self, pg_loader, etl_loader):
        genres = pg_loader.get_genres_all()

        etl_loader.bulk_load_genres(genres=genres)
        logger.info(f"Загрузка индекса genres - успешно загружено {len(genres)} жанров")

def main():
    time.sleep(60)
    warnings.simplefilter("ignore", category=ElasticsearchWarning)

    es = Elasticsearch(
        [
            {
                "host": settings.ETL_HOST,
                "port": settings.ETL_PORT,
                "scheme": settings.ETL_SCHEMA
            }
        ]
    )

    es_loader = ElasticsearchLoader(es=es)
    pg_loader = PostgresLoader()

    etl_loader = EtlLoader(es)

    for index in ['movies', 'persons', 'genres']:
        etl_loader.create_index(index)

    connection = connect_to_db()
    try:
        with db_session(connection=connection) as cur:
            while True:
                pg_loader = PostgresLoader(cursor=cur)

                index_loader.load_movies_index(pg_loader, es_loader)
                index_loader.load_persons_index(pg_loader, es_loader)
                index_loader.load_genres_index(pg_loader, etl_loader)

    except Exception as _exc:
        logger.error(f"ERROR: {_exc}")
    finally:
        connection.close()
        es.transport.close()

if __name__ == "__main__":
    main()
