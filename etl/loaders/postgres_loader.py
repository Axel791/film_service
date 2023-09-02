from typing import List

from pydantic import UUID4

from schemas.film_work_to_es import FilmWorkES
from schemas.genres import Genre
from schemas.person_filmworks import PersonFilmWork
from schemas.person_to_es import PersonES
from schemas.persons import Person
from utils.query import (FILM_WORK_QUERY_ALL, GENRE_QUERY, GENRE_QUERY_ALL,
                         PERSON_FILM_WORK_QUERY, PERSON_QUERY,
                         PERSON_QUERY_ALL)


class PostgresLoader:
    def __init__(self, cursor) -> None:
        self._cursor = cursor

    def get_film_works_all(self) -> List[FilmWorkES]:
        self._cursor.execute(FILM_WORK_QUERY_ALL)
        rows = self._cursor.fetchall()

        film_works = []
        for row in rows:
            film_work = FilmWorkES(
                id=row[0],
                title=row[1],
                description=row[2],
                type=row[3],
                creation_date=row[4],
                imdb_rating=row[5],
            )
            film_works.append(film_work)

        return film_works

    def get_genres_by_fw_id(self, film_work_id: UUID4) -> List[Genre]:
        self._cursor.execute(GENRE_QUERY, (str(film_work_id),))
        rows = self._cursor.fetchall()

        genres = []
        for row in rows:
            genre = Genre(
                id=row[0],
                name=row[1],
                description=row[2],
            )
            genres.append(genre)

        return genres

    def get_persons_by_fw_id(self, film_work_id: UUID4) -> List[Person]:
        self._cursor.execute(PERSON_QUERY, (str(film_work_id),))
        rows = self._cursor.fetchall()
        persons = []
        for row in rows:
            person = Person(
                id=row[0],
                full_name=row[1],
                role=row[2],
            )
            persons.append(person)

        return persons

    def get_persons_all(self) -> List[PersonES]:
        self._cursor.execute(PERSON_QUERY_ALL)
        rows = self._cursor.fetchall()

        persons = []
        for row in rows:
            person = PersonES(id=row[0], full_name=row[1])
            persons.append(person)

        return persons

    def get_film_works_by_p_id(self, person_id: UUID4) -> List[PersonFilmWork]:
        self._cursor.execute(PERSON_FILM_WORK_QUERY, (str(person_id),))
        rows = self._cursor.fetchall()
        film_works = []
        for row in rows:
            film_work = PersonFilmWork(id=row[0], title=row[1], role=row[2])
            film_works.append(film_work)

        return film_works

    def get_genres_all(self) -> List[Genre]:
        self._cursor.execute(GENRE_QUERY_ALL)
        rows = self._cursor.fetchall()

        genres = []
        for row in rows:
            genre = Genre(id=row[0], name=row[1], description=row[2])
            genres.append(genre)

        return genres
