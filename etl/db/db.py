import psycopg2

from .backoff import backoff
from core.config import settings


@backoff()
def connect_to_db():
    conn = psycopg2.connect(**settings.DATABASE_URI)
    return conn
