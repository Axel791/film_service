import random
import time
import uuid
from datetime import datetime, timedelta

from vertica_python import connect as vertica_connect
from clickhouse_driver import Client


def generate_data(n):
    """Функция для генерации данных"""
    data = []
    for i in range(n):
        user_id = uuid.uuid4()
        film_id = uuid.uuid4()
        film_timestamp = random.randint(1, 1000)
        event_time = datetime.now() - timedelta(days=random.randint(0, 10))
        event_date_part = event_time.date()
        data.append((user_id, film_id, film_timestamp, event_time, event_date_part))
    return data


def measure_time(func, *args, **kwargs):
    """Функция для тестирования выполнения времени"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time, result


def create_table(db_name, connection):
    """Функция для создания таблицы"""
    print(f"Создаем таблицу {db_name}...")
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS views (
            id IDENTITY,
            user_id uuid NOT NULL,
            film_id uuid NOT NULL,
            film_timestamp integer NOT NULL,
            event_time timestamp NOT NULL,
            event_date_part date NOT NULL)
    """
    connection.execute(create_table_sql)


def test_insert(db_name, connection, data):
    """Функция тестирования вставки данных в таблицу"""
    print(f"Тестируем вставку: {db_name}...")
    insert_sql = """
        INSERT INTO views (user_id, film_id, film_timestamp, event_time, event_date_part)
        VALUES (?, ?, ?, ?, ?)
    """
    insert_time, _ = measure_time(connection.executemany, insert_sql, data)
    print(f"{db_name} - Время вставки для {len(data)} строк: {insert_time} секунд")


def test_select(db_name, connection, data):
    """Функция для тестирования чтения данных с фильтрацией по user_id"""
    print(f"Тестируем фильтрацию: {db_name}...")
    user_id = data[0][0] # Просто берем первый user_id из данных
    select_sql = f"SELECT * FROM views WHERE user_id = '{user_id}'"
    select_time, _ = measure_time(connection.execute, select_sql)
    print(f"{db_name} - Результаты теста для {user_id}: {select_time} секунд")


if __name__ == "__main__":
    # Генерация 10 миллионов записей
    data = generate_data(10000000)

    # Тестирование Vertica
    vertica_connection = vertica_connect(
        host='localhost',
        port=5433,
        user='your_user',
        password='your_password',
        database='your_database'
    )
    create_table('Vertica', vertica_connection)
    test_insert('Vertica', vertica_connection, data)
    test_select('Vertica', vertica_connection, data)
    vertica_connection.close()

    # Тестирование ClickHouse
    clickhouse_client = Client('localhost')
    create_table('ClickHouse', clickhouse_client)
    test_insert('ClickHouse', clickhouse_client, data)
    test_select('ClickHouse', clickhouse_client, data)
    clickhouse_client.disconnect()
