from datetime import datetime, timedelta
from typing import List

from auth.core.config import settings
from auth.repository.login_event import RepositoryLoginEvent
from auth.repository.user import RepositoryUser
from auth.repository.user_provider import UserProvider
from auth.schemas.login_event import LoginEvent
from auth.schemas.token import Token
from auth.schemas.user import RegUserIn
from auth.utils.check_jwt_token import CheckToken

from fastapi import Depends, HTTPException, status
from jose import jwt
from loguru import logger
from passlib.context import CryptContext
from redis.asyncio import Redis

from utils.check_jwt_token import check_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    ALGORITHM = settings.algorithm
    SECRET_KEY = settings.jwt_secret_key
    REFRESH_SECRET_KEY = settings.jwt_refresh_secret_key
    REFRESH_TOKEN_EXPIRE = settings.refresh_token_expire
    ACCESS_TOKEN_EXPIRE = settings.access_token_expire

    def __init__(
            self,
            repository_user: RepositoryUser,
            repository_login_event: RepositoryLoginEvent,
            repository_user_provider: UserProvider,
            redis: Redis,
    ):
        self._repository_user = repository_user
        self._repository_login_event = repository_login_event
        self._repository_user_provider = repository_user_provider
        self._redis = redis

    def create_access_token(self, user_login: str) -> str:
        expiry = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE)
        payload = {"sub": user_login, "exp": expiry}
        access_token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return access_token

    def create_refresh_token(self, user_login: str) -> str:
        expiry = datetime.utcnow() + timedelta(minutes=self.REFRESH_TOKEN_EXPIRE)
        payload = {"sub": user_login, "exp": expiry}
        refresh_token = jwt.encode(
            payload, self.REFRESH_SECRET_KEY, algorithm=self.ALGORITHM
        )
        return refresh_token

    def _get_password_hash(self, password):
        return pwd_context.hash(password)

    def verify_password(self, input_password, hashed_password):
        return pwd_context.verify(input_password, hashed_password)

    def _send_login_event(self, user_id, login_success):
        login_event = {"user_id": user_id, "login_success": login_success}
        self._repository_login_event.create(obj_in=login_event)

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
            "password": hashed_password
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
                input_password=form_data.password, hashed_password=user.password
        ):
            logger.warning(f"Invalid password for user {user.login}.")
            self._send_login_event(user.id, False)
            raise credentials_exception

        refresh_token = self.create_refresh_token(user_login=user.login)
        access_token = self.create_access_token(user_login=user.login)
        await self._redis.set(user.login, access_token)
        self._send_login_event(user.id, True)
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
            decoded_token = jwt.decode(
                access_token.token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
        except jwt.JWTError:
            logger.warning("Invalid token during access token refresh.")
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_login = decoded_token.login
        stored_access_token = await self._redis.get(user_login)
        if stored_access_token != access_token.token:
            logger.warning(f"Invalid access token for user {user_login}.")
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = self._repository_user.get(login=user_login)
        refresh_token = jwt.decode(
            user.token, self.REFRESH_SECRET_KEY, algorithms=[self.ALGORITHM]
        )

        if refresh_token["exp"] > datetime.utcnow():
            new_access_token = self.create_access_token(user_login=user_login)
            await self._redis.set(user.login, new_access_token)
            logger.info(f"Access token refreshed for user {user.login}.")
        else:
            logger.warning(f"Refresh token expired for user {user.login}.")
            raise HTTPException(
                status_code=401,
                detail="Refresh token expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return Token(token=new_access_token)

    async def check_authorisation(self, token: str) -> CheckToken:
        token_data: CheckToken = check_token(secret=settings.jwt_secret_key, token=token)
        return token_data

    async def get_login_history(
            self,
            user_login: str,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size,
    ) -> List[LoginEvent]:
        user = self._repository_user.get(login=user_login)
        login_history = self._repository_login_event.list(
            user_id=user.id, skip=page, offset=page_size
        )
        logger.info(f"Login history retrieved for user {user.login}.")
        return login_history

    def store_provider_data(self):
        pass