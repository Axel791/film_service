FILM_WORK_QUERY_ALL = """
SELECT id, title, description, type, creation_date, rating
FROM content.film_work
"""

GENRE_QUERY = """
SELECT genre.id, genre.name, genre.description
FROM content.genre
JOIN content.genre_film_work ON genre.id = genre_film_work.genre_id
WHERE content.genre_film_work.film_work_id = %s
"""

PERSON_QUERY = """
SELECT person.id, person.full_name, person_film_work.role
FROM content.person
JOIN content.person_film_work ON person.id = person_film_work.person_id
WHERE person_film_work.film_work_id = %s
"""

PERSON_QUERY_ALL = """
SELECT id, full_name
FROM content.person
"""

PERSON_FILM_WORK_QUERY = """
SELECT film_work.id, film_work.title, person_film_work.role
FROM content.film_work
JOIN content.person_film_work ON film_work.id = person_film_work.film_work_id
WHERE person_film_work.person_id = %s
"""

GENRE_QUERY_ALL = """
SELECT id, name, description
FROM content.genre
"""
