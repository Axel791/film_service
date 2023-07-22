from functools import wraps
from uuid import uuid4

from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

from auth.core.containers import Container
from auth.db.session import scope
from auth.core.config import settings

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
        username: str = payload.get("email")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = rep_user.get(email=username)
    if user is None:
        raise credentials_exception
    return user


@inject
async def create_session():
    scope.set(str(uuid4()))


@inject
def commit_and_close_session(func):

    @wraps(func)
    @inject
    async def wrapper(db=Depends(Provide[Container.db]), *args, **kwargs,):
        scope.set(str(uuid4()))
        try:
            result = await func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise e
        finally:
            # db.session.expunge_all()
            db.scoped_session.remove()

    return wrapper
