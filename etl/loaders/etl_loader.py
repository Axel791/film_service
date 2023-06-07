from schemas.film_work_to_es import FilmWorkES
from schemas.person_to_es import PersonES
from schemas.genres import Genre

from typing import List

from elasticsearch import helpers, Elasticsearch

from utils.index import INDEX_SETTINGS
from db.backoff import backoff


class ElasticsearchLoader:

    def __init__(self, es: Elasticsearch) -> None:
        self._es = es

    @backoff()
    def create_index(self, index: str):
        if not self._es.indices.exists(index=index):
            self._es.indices.create(
                index=index,
                settings=INDEX_SETTINGS.get('settings'),
                mappings=INDEX_SETTINGS.get(index).get('mappings')
            )

    def bulk_load_film_works(self, film_works: List[FilmWorkES]):
        actions = []
        for film_work in film_works:
            doc = {
                "_index": "movies",
                "_id": str(film_work.id),
                "_source": {
                    "id": str(film_work.id),
                    "imdb_rating": film_work.imdb_rating,
                    "genre": film_work.genres,
                    "title": film_work.title,
                    "description": film_work.description,
                    "director": ' '.join(film_work.director),
                    "actors_names": ' '.join(film_work.actors_names),
                    "writers_names": ' '.join(film_work.writers_names),
                    "actors": film_work.actors,
                    "writers": film_work.writers
                }
            }
            actions.append(doc)
        helpers.bulk(self._es, actions)

    def bulk_load_persons(self, persons: List[PersonES]):
        actions = []
        for person in persons:
            doc = {
                "_index": "persons",
                "_id": str(person.id),
                "_source": {
                    "id": str(person.id),
                    "full_name": person.full_name,
                    "films": person.films
                }
            }
            print(doc)
            actions.append(doc)
        helpers.bulk(self._es, actions)

    def bulk_load_genres(self, genres: List[Genre]):
        actions = []
        for genre in genres:
            doc = {
                "_index": "genres",
                "_id": str(genre.id),
                "_source": {
                    "id": str(genre.id),
                    "name": genre.name,
                    "description": genre.description
                }
            }
            print(doc)
            actions.append(doc)
        helpers.bulk(self._es, actions)

