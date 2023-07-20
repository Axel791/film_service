from .base import RepositoryBase
from auth.models.entity import User


class RepositoryUser(RepositoryBase[User]):
    pass
