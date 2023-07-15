import json

from dependency_injector import containers, providers


from auth.core.config import Settings
from auth.db.session import SyncSession
from auth.db.init_redis import redis


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)

    db = providers.Singleton(SyncSession, db_url=config.provided.sync_sqlalchemy_database_uri)

    redis = providers.Resource(
        redis.get_redis,
        host=config.provided.REDIS_HOST,
        port=config.provided.REDIS_HOST
    )


