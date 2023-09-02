from typing import Any, Dict, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    ETL_HOST: str
    ETL_PORT: int
    ETL_SCHEMA: str

    DATABASE_URI: Optional[dict] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[dict], values: Dict[str, Any]) -> Any:
        if isinstance(v, dict):
            return v
        return {
            "dbname": values.get("DB_NAME"),
            "user": values.get("DB_USER"),
            "password": values.get("DB_PASSWORD"),
            "host": values.get("DB_HOST"),
            "port": values.get("DB_PORT"),
        }

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
