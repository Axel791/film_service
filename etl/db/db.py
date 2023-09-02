import psycopg2

from core.config import settings

from .backoff import backoff


@backoff()
def connect_to_db():
    conn = psycopg2.connect(**settings.DATABASE_URI)
    return conn
