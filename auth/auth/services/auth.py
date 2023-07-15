from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt
from loguru import logger

from passlib.context import CryptContext
from auth.models.entity import User

from auth.core.config import settings
from auth.schemas.auth import RegUserIn
from auth.repository.base import RepositoryBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    ALGORITHM = settings.AlGORITHM
    SECRET_KEY = settings.JWT_SECRET_KEY
    REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
    REFRESH_TOKEN_EXPIRE_MINS = settings.REFRESH_TOKEN_EXPIRE_MINS
    ACCESS_TOKEN_EXPIRE_MINS = settings.ACCESS_TOKEN_EXPIRE_MINS

    def __init__(
            self,
            repository: RepositoryBase,
    ):
        self._repository_user = repository(User)

    def create_access_token(self, user: User) -> str:
        expiry = datetime.utcnow() + timedelta(mins=self.ACCESS_TOKEN_EXPIRE_MINS)
        payload = {
            "login": user.login,
            "exp": expiry,
        }
        access_token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return access_token

    def create_refresh_token(self, user: User) -> str:
        expiry = datetime.utcnow() + timedelta(mins=self.REFRESH_TOKEN_EXPIRE_MINS)
        payload = {
            "login": user.login,
            "exp": expiry,
        }
        refresh_token = jwt.encode(payload, self.REFRESH_SECRET_KEY, algorithm=self.ALGORITHM)
        return refresh_token

    def _get_password_hash(self, password):
        return pwd_context.hash(password)

    def verify_password(self, input_password, hashed_password):
        return pwd_context.verify(input_password, hashed_password)

    async def registration(self, user: RegUserIn):
        user_login = self._repository_user.get(login=user.login)
        user_email = self._repository_user.get(email=user.email)
        if user_email is not None:
            raise ValueError("Такой email уже зарегистрирован.")
        if user_login is not None:
            raise ValueError("Такой логин уже зарегистрирован.")

        hashed_password = self._get_password_hash(password=user.password)
        refresh_token = self.create_refresh_token(user=user)
        access_token = self.create_access_token(user=user)

        obj_in = {
            "token": refresh_token,
            "login": user.login,
            "email": user.email,
            "password": hashed_password,
            "secret_key": "secret"
        }
        logger.info(obj_in)

        return self._repository_user.create(obj_in=obj_in)

    async def login(self, form_data):
        credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = self._repository_user.get(email=form_data.username)
        if not user:
            raise credentials_exception
        if not self.verify_password(
            input_password=form_data.password,
            hashed_password=user.password
        ):
            raise credentials_exception

        refresh_token = self.create_refresh_token(user=user)
        access_token = self.create_access_token(user=user)
        logger.info(refresh_token)

        return {"refresh_token": refresh_token, "token_type": "bearer"}


