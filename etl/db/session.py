import logging

from psycopg2.extras import DictCursor
from contextlib import contextmanager


@contextmanager
def db_session(connection):
    cursor = connection.cursor(cursor_factory=DictCursor)
    try:
        yield cursor
        connection.commit()
    except Exception as _exc:
        logging.info(f"Ошибка при выполнении транзакции: {_exc}, откат изменений")
        connection.rollback()
        raise
    finally:
        cursor.close()
