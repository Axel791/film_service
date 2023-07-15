from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from auth.models.entity import User
from loguru import logger
from auth.core.config import settings
from auth.schemas.auth import RegUserIn, ChangeIn
from auth.repository.base import RepositoryBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    ALGORITHM = settings.AlGORITHM
    SECRET_KEY = settings.JWT_SECRET_KEY

    def __init__(
            self,
            repository: RepositoryBase,
    ):
        self._repository_user = repository(User)

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_jwt

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
        access_token = self.create_access_token(data={"login": user.login})
        obj_in = {
            "token": access_token,
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

        access_token = self.create_access_token(
            data={"email": user.email}
        )
        logger.info(access_token)
        return {"access_token": access_token, "token_type": "bearer"}


