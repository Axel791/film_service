from .base import RepositoryBase
from auth.models.login_event import LoginEvent


class RepositoryLoginEvent(RepositoryBase[LoginEvent]):
    pass
