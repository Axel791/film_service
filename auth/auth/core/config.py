from pydantic import PostgresDsn, BaseSettings, validator

from typing import Any, Dict


class Settings(BaseSettings):
    PROJECT_SLUG: str
    API_V1_STR: str

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    REDIS_PORT: str
    REDIS_HOST: str

    JAEGER_HOST: str
    JAEGER_PORT: int

    ASYNC_SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None
    SYNC_SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    AlGORITHM: str

    default_page_size: int = 10

    @validator("ASYNC_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_async_db_connection(cls, v: str | None, values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path=f"/{values.get('DB_NAME') or ''}",
        )

    @validator("SYNC_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_sync_db_connection(cls, v: str | None, values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path=f"/{values.get('DB_NAME') or ''}",
        )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
