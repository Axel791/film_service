from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException, status
from jose import jwt
from loguru import logger
from redis.asyncio import Redis

from passlib.context import CryptContext

from auth.core.config import settings
from auth.schemas.user import RegUserIn
from auth.schemas.token import Token
from auth.schemas.login_event import LoginEvent
from auth.repository.user import RepositoryUser
from auth.repository.login_event import RepositoryLoginEvent

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    ALGORITHM = settings.AlGORITHM
    SECRET_KEY = settings.JWT_SECRET_KEY
    REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
    REFRESH_TOKEN_EXPIRE = settings.REFRESH_TOKEN_EXPIRE
    ACCESS_TOKEN_EXPIRE = settings.ACCESS_TOKEN_EXPIRE

    def __init__(
            self,
            repository_user: RepositoryUser,
            repository_login_event: RepositoryLoginEvent,
            redis: Redis
    ):
        self._repository_user = repository_user
        self._repository_login_event = repository_login_event
        self._redis = redis

    def create_access_token(self, user_login: str) -> str:
        expiry = datetime.utcnow() + timedelta(mins=self.ACCESS_TOKEN_EXPIRE_MINS)
        payload = {
            "login": user_login,
            "exp": expiry,
        }
        access_token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return access_token

    def create_refresh_token(self, user_login: str) -> str:
        expiry = datetime.utcnow() + timedelta(mins=self.REFRESH_TOKEN_EXPIRE_MINS)
        payload = {
            "login": user_login,
            "exp": expiry
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
        refresh_token = self.create_refresh_token(user_login=user_login)
        access_token = self.create_access_token(user_login=user_login)
        await self._redis.set(user_login, access_token)
        obj_in = {
            "token": refresh_token,
            "login": user.login,
            "email": user.email,
            "password": hashed_password,
            "secret_key": "secret"
        }
        logger.info(obj_in)

        return await self._repository_user.create(obj_in=obj_in)

    async def login(self, form_data):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        user = self._repository_user.get(email=form_data.user_email)
        if not user:
            logger.warning(f"User with email {form_data.user_email} not found.")
            raise credentials_exception
        if not self.verify_password(
                input_password=form_data.password,
                hashed_password=user.password
        ):
            logger.warning(f"Invalid password for user {user.login}.")
            raise credentials_exception

        refresh_token = self.create_refresh_token(user_login=user.login)
        access_token = self.create_access_token(user_login=user.login)
        await self._redis.set(user.login, access_token)
        logger.info(f"User {user.login} logged in.")
        logger.debug(f"Generated refresh token: {refresh_token}")
        return {
            "token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "login": user.login,
                "password": user.password,
                "email": user.email,
                "role": user.role,
                "user_id_role": user.user_role_id,
                "created_at": user.created_at,
                "token": user.token,
            }
        }

    async def refresh_access_token(self, access_token: Token) -> Token:
        try:
            decoded_token = jwt.decode(access_token.token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except jwt.JWTError:
            logger.warning("Invalid token during access token refresh.")
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_login = decoded_token.login
        stored_access_token = await self._redis.get(user_login)
        if stored_access_token != access_token:
            logger.warning(f"Invalid access token for user {user_login}.")
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = self._repository_user.get(login=user_login)
        refresh_token = jwt.decode(user.token, self.REFRESH_SECRET_KEY, algorithms=[self.ALGORITHM])

        if refresh_token.exp > datetime.utcnow():
            new_access_token = self.create_access_token(user)
            self._redis.set(user_login, new_access_token)
            logger.info(f"Access token refreshed for user {user.login}.")
        else:
            logger.warning(f"Refresh token expired for user {user.login}.")
            raise HTTPException(
                status_code=401,
                detail="Refresh token expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return new_access_token

    async def get_login_history(self, user_login: str,
                                page: int | None = 1,
                                page_size: int | None = settings.default_page_size) -> List[LoginEvent]:
        user = self._repository_user.get(login=user_login)
        login_history = self._repository_login_event.list(user_id=user.id, skip=page, offset=page_size)
        logger.info(f"Login history retrieved for user {user.login}.")
        return login_history


