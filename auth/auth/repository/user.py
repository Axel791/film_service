from .base import RepositoryBase
from auth.models.entity import User


class RepositoryUser(RepositoryBase[User]):
    def get_user(self):
        pass