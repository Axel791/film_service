import time
from core.config import settings
import redis

if __name__ == '__main__':
    redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port)

    while True:
        try:
            redis_client.ping()
            break
        except redis.ConnectionError:
            time.sleep(1)
