import logging
import time


def backoff(max_retries=5, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as _exc:
                    print("error")
                    print(_exc)
                    logging.info(
                        f"Ошибка: {_exc}, повторное подключение через {delay} секунды. Попытка {retries + 1} из {max_retries}"
                    )
                    time.sleep(delay)
                    retries += 1
            raise Exception("Превышено максимальное количество попыток подключения")

        return wrapper

    return decorator
