from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

from auth.core.config import settings
from auth.models import User
from auth.db import session
from auth.schemas import Token, TokenPayload, UserCreate, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def authenticate_user(self, username: str, password: str) -> UserInDB:
        user = session.query(User).filter(User.username == username).first()
        if not user or not pwd_context.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserInDB.from_orm(user)

    def create_access_token(self, user: UserInDB) -> Token:
        expiry = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": expiry,
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.algorithm)
        return Token(access_token=token, token_type="bearer")

    def create_user(self, user_data: UserCreate) -> UserInDB:
        user = User(
            username=user_data.username,
            password=self.hash_password(user_data.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return UserInDB.from_orm(user)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.algorithm],
            )
            return TokenPayload(**payload)
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
