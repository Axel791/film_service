import warnings
import time
from loguru import logger

from elasticsearch.exceptions import ElasticsearchWarning

from db.session import db_session
from db.db import connect_to_db

from loaders.etl_loader import ElasticsearchLoader
from loaders.postgres_loader import PostgresLoader

from utils.data_states import state

from core.config import settings

from elasticsearch import Elasticsearch

es = Elasticsearch(
    [
        {
            "host": settings.ETL_HOST,
            "port": settings.ETL_PORT,
            "scheme": settings.ETL_SCHEMA
        }
    ]
)

if __name__ == "__main__":
    warnings.simplefilter("ignore", category=ElasticsearchWarning)

    etl_loader = ElasticsearchLoader(es=es)
    for index in ['movies', 'persons', 'genres']:
        etl_loader.create_index(index)

    connection = connect_to_db()
    try:
        with db_session(connection=connection) as cur:
            last_position_films = state.get_state("last_position_films") or 0
            last_position_persons = state.get_state("last_position_persons") or 0
            last_position_genres = state.get_state("last_position_genres") or 0
            while True:
                pg_loader = PostgresLoader(cursor=cur)

                # loading movies index
                film_works = pg_loader.get_film_works_all()
                for film_i, film_work in enumerate(film_works[last_position_films:], start=last_position_films):
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

                # loading persons index
                persons = pg_loader.get_persons_all()
                for person_i, person in enumerate(persons[last_position_persons:], start=last_position_persons):
                    all_film_works = pg_loader.get_film_works_by_p_id(person.id)
                    person.films = [
                        {
                            "id": film_work.id,
                            "title": film_work.title,
                            "roles": film_work.role
                        } for film_work in all_film_works
                    ]

                # loading genres index
                genres = pg_loader.get_genres_all()

                #load data to elastic
                try:
                    etl_loader.bulk_load_film_works(film_works=film_works)
                    etl_loader.bulk_load_persons(persons=persons)
                    etl_loader.bulk_load_genres(genres=genres)
                    state.set_state("last_position_movies", film_i + 1)
                    state.set_state("last_position_persons", person_i + 1)
                    state.set_state("last_position_genres", len(genres) + 1)
                except Exception as _exc:
                    logger.error(f"Ошибка загрузки данных на: {film_i}: {_exc}")
                    break
                time.sleep(60)
    except Exception as _exc:
        logger.error(f"ERROR: {_exc}")
    finally:
        connection.close()
        es.transport.close()
