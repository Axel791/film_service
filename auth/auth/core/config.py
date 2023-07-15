from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, field_validator

from typing import Any, Dict


class Settings(BaseSettings):
    PROJECT_SLUG: str
    api_v1_str: str

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str

    REDIS_PORT: str
    REDIS_HOST: str

    ASYNC_SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None
    SYNC_SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ALGORITHM: str

    @field_validator("ASYNC_SQLALCHEMY_DATABASE_URI")
    def assemble_async_db_connection(cls, v: str | None, values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("db_user"),
            password=values.get("db_password"),
            host=values.get("db_host"),
            port=values.get("db_port"),
            path=f"/{values.get('db_name') or ''}",
        )

    @field_validator("SYNC_SQLALCHEMY_DATABASE_URI")
    def assemble_sync_db_connection(cls, v: str | None, values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("db_user"),
            password=values.get("db_password"),
            host=values.get("db_host"),
            port=values.get("db_port"),
            path=f"/{values.get('db_name') or ''}",
        )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
