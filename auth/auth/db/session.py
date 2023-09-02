from contextvars import ContextVar

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

scope: ContextVar = ContextVar("db_session_scope")


def scopefunc():
    try:
        return scope.get()
    except LookupError:
        logger.warning("scope not set")
        return None


# for fastapi
class SyncSession:
    def __init__(self, db_url: str, dispose_session: bool = False):
        self.db_url = db_url
        self.dispose_session = dispose_session
        self.sync_engine = create_engine(self.db_url, pool_pre_ping=True)
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine, autoflush=False, expire_on_commit=False
        )
        self.scoped_session = scoped_session(
            self.sync_session_factory, scopefunc=scopefunc
        )
        self.session = self.scoped_session()
        logger.info("SyncSession initialized with DB URL: %s", self.db_url)

    def __del__(self):
        if self.dispose_session:
            self.session.remove()
            logger.debug("SyncSession disposed and session removed")

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.dispose_session:
            logger.warning(
                "Session not disposed explicitly. Please make sure to call `.dispose()` when done."
            )
        self.session.remove()
        logger.debug("SyncSession exited and session removed")

    def dispose(self):
        self.session.remove()
        logger.info("SyncSession disposed and session removed")
