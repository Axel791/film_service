from functools import wraps
from uuid import uuid4

from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from auth.core.containers import Container
from auth.db.session import scope
from auth.core.config import settings

from loguru import logger

from auth.models.roles import Permissions
from auth.utils import errors_const

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/api/v1/auth/login")

SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY


@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    rep_user=Depends(Provide[Container.repository_user])
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("login")
        if username is None:
            raise credentials_exception
    except JWTError:
        logger.exception("JWTError while decoding token")
        raise credentials_exception

    user = rep_user.get(email=username)
    if user is None:
        logger.warning("User with email %s not found", username)
        raise credentials_exception

    return user


@inject
async def filter_user_superuser(
        user=Depends(get_current_user),
        rep_user=Depends(Provide[Container.repository_user])
):
    user = rep_user.get(id=user.id)
    if user.role.permission_class == Permissions.ALL:
        return user
    raise HTTPException(
        status_code=400,
        detail=errors_const.PERMISSION_ERROR
    )


@inject
async def filter_user_moderator(
        user=Depends(get_current_user),
        rep_user=Depends(Provide[Container.repository_user])
):
    user = rep_user.get(id=user.id)
    if user.role.permission_class in [Permissions.MEDIUM, Permissions.ALL]:
        return user
    raise HTTPException(
        status_code=400,
        detail=errors_const.PERMISSION_ERROR
    )


@inject
async def filter_user_subs(
        user=Depends(get_current_user),
        rep_user=Depends(Provide[Container.repository_user])
):
    user = rep_user.get(id=user.id)
    if user.role.permission_class in [
        Permissions.MEDIUM,
        Permissions.SOME,
        Permissions.ALL
    ]:
        return user
    raise HTTPException(
        status_code=400,
        detail=errors_const.PERMISSION_ERROR
    )


@inject
async def create_session():
    session_id = str(uuid4())
    scope.set(session_id)
    logger.info("Session created with ID: %s", session_id)


@inject
def commit_and_close_session(func):

    @wraps(func)
    @inject
    async def wrapper(db=Depends(Provide[Container.db]), *args, **kwargs):
        session_id = str(uuid4())
        scope.set(session_id)
        logger.info("Session created with ID: %s", session_id)

        try:
            result = await func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            logger.exception("Exception occurred during request processing: %s", str(e))
            db.session.rollback()
            raise e
        finally:
            # db.session.expunge_all()
            db.scoped_session.remove()
            logger.info("Session with ID %s closed", session_id)

    return wrapper
