from pydantic import BaseSettings, PostgresDsn, validator

from typing import Any, Dict


class Settings(BaseSettings):
    project_slug: str
    api_v1_str: str

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str

    async_sqlalchemy_database_uri: PostgresDsn | None = None
    sync_sqlalchemy_database_uri: PostgresDsn | None = None

    @validator("ASYNC_SQLALCHEMY_DATABASE_URI", pre=True)
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

    @validator("SYNC_SQLALCHEMY_DATABASE_URI", pre=True)
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
