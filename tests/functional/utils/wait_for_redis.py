import time
from settings import test_settings

import redis

if __name__ == '__main__':
    redis_client = redis.Redis(host=test_settings.redis_host, port=test_settings.redis_port)

    while True:
        try:
            redis_client.ping()
            break
        except redis.ConnectionError:
            time.sleep(1)
