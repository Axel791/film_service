from dependency_injector import containers, providers


from auth.core.config import Settings
from auth.db.session import SyncSession
from auth.db import init_redis

from auth.models.entity import User
from auth.models.roles import Role

from auth.repository.user import RepositoryUser
from auth.repository.role import RepositoryRole

from auth.services.auth_service import AuthService
from auth.services.role_service import RoleService


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)

    db = providers.Singleton(SyncSession, db_url=config.provided.SYNC_SQLALCHEMY_DATABASE_URI)

    redis = providers.Resource(
        init_redis.init_redis_pool,
        host=config.provided.REDIS_HOST
    )

    repository_user = providers.Singleton(RepositoryUser,  model=User, session=db)
    repository_role = providers.Singleton(RepositoryRole, model=Role, session=db)

    role_service = providers.Singleton(
        RoleService,
        repository_user=repository_user,
        repository_role=repository_role,
    )

    auth_service = providers.Singleton(
        AuthService,
        repository_user=repository_user,
        redis=redis,
    )


