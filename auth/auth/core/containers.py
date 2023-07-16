import json

from dependency_injector import containers, providers


from auth.core.config import Settings
from auth.db.session import SyncSession
from auth.db import init_redis

from auth.services.auth_service import AuthService


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)

    db = providers.Singleton(SyncSession, db_url=config.provided.sync_sqlalchemy_database_uri)

    redis = providers.Resource(
        init_redis.redis,
        host=config.provided.REDIS_HOST,
        port=config.provided.REDIS_HOST
    )

    auth_service = providers.Singleton(
        AuthService
    )


