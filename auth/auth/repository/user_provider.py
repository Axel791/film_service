from .base import RepositoryBase
from auth.models.user_provider import UserProvider


class RepositoryUserProvider(RepositoryBase[UserProvider]):
    pass
