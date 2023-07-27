from pydantic import PostgresDsn, BaseSettings, validator

from typing import Any, Dict


class Settings(BaseSettings):
    project_slug: str
    api_v1_str: str

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str

    redis_port: str
    redis_host: str
    redis_db_for_rate_limiter: int = 1

    jaeger_host: str
    jaeger_port: int

    async_sqlalchemy_database_uri: PostgresDsn | None = None
    sync_sqlalchemy_database_uri: PostgresDsn | None = None

    access_token_expire: int
    refresh_token_expire: int
    jwt_secret_key: str
    jwt_refresh_secret_key: str
    algorithm: str

    google_cid: str
    google_secret: str
    google_discovery_url: str

    default_page_size: int = 10

    requests_limit_per_min: int = 20

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
