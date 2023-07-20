from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt
from loguru import logger
from redis.asyncio import Redis

from passlib.context import CryptContext
from auth.models.entity import User

from auth.core.config import settings
from auth.schemas.user import RegUserIn
from auth.schemas.token import Token
from auth.repository.user import RepositoryUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    ALGORITHM = settings.AlGORITHM
    SECRET_KEY = settings.JWT_SECRET_KEY
    REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
    REFRESH_TOKEN_EXPIRE_MINS = 30
    ACCESS_TOKEN_EXPIRE_MINS = 60 * 24 * 7

    def __init__(
            self,
            repository_user: RepositoryUser,
            redis: Redis
    ):
        self._repository_user = repository_user
        self._redis = redis

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
            "exp": expiry
        }
        refresh_token = jwt.encode(payload, self.REFRESH_SECRET_KEY, algorithm=self.ALGORITHM)
        return refresh_token

    def _get_password_hash(self, password):
        return pwd_context.hash(password)

    def verify_password(self, input_password, hashed_password):
        return pwd_context.verify(input_password, hashed_password)

    async def registration(self, redis: Redis, user: RegUserIn):
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

        return {"token": refresh_token, "token_type": "bearer"}

    async def refresh_access_token(self, access_token: Token) -> Token:
        try:
            decoded_token = jwt.decode(access_token.token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_login = decoded_token.login
        stored_access_token = await self._redis.get(user_login)
        if stored_access_token != access_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = self._repository_user.get(login=user_login)
        refresh_token = jwt.decode(user.token, self.REFRESH_SECRET_KEY, algorithms=[self.ALGORITHM])

        if refresh_token.exp > datetime.utcnow():
            new_access_token = self.create_access_token(user)
            await self._redis.set(user_login, new_access_token)
        else:
            print("access token is fine")
            # перенаправить пользователя на логин опять
        return new_access_token
