from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from jose import jwt
from redis import Redis
from sqlalchemy.orm import Session

from auth.core.config import settings
from auth.models import User
from auth.db import SessionLocal
from auth.schemas import Token, UserCreate, UserInDB

router = APIRouter()

class AuthService:
    def __init__(self, db: Session, redis_client: Redis):
        self.db = db
        self.redis_client = redis_client

    def authenticate_user(self, username: str, password: str) -> UserInDB:
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not user.verify_password(password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserInDB.from_orm(user)

    def create_access_token(self, user: UserInDB) -> Token:
        expiry = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": expiry,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return Token(access_token=token, token_type="bearer")

    def verify_access_token(self, access_token: str) -> UserInDB:
        try:
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            user_id = payload["sub"]
            username = payload["username"]

            # Verify if the access token matches the one stored in Redis
            stored_access_token = self.redis_client.get(username)
            if stored_access_token != access_token.encode():
                raise HTTPException(
                    status_code=401,
                    detail="Invalid access token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Retrieve the user from the database
            user = self.db.query(User).get(user_id)
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid user",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return UserInDB.from_orm(user)

        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_refresh_token(self, refresh_token: str) -> UserInDB:
        user_id = self.redis_client.get(refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = self.db.query(User).get(user_id)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserInDB.from_orm(user)



