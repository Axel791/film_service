import logging
from contextlib import contextmanager

from psycopg2.extras import DictCursor


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
