from dependency_injector import containers, providers


from auth.core.config import Settings
from auth.db.session import SyncSession
from auth.db import init_redis

from auth.models.entity import User

from auth.repository.user import RepositoryUser

from auth.services.auth_service import AuthService


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)

    db = providers.Singleton(SyncSession, db_url=config.provided.sync_sqlalchemy_database_uri)

    redis = providers.Resource(
        init_redis.init_redis_pool,
        host=config.provided.REDIS_HOST,
        port=config.provided.REDIS_HOST
    )

    repository_user = providers.Singleton(RepositoryUser,  model=User, session=db)

    auth_service = providers.Singleton(
        AuthService,
        repository_user=repository_user,
        redis=redis,
    )


