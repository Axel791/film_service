from typing import Any, Dict, Optional
from pydantic import BaseSettings, RedisDsn, validator


class Settings(BaseSettings):
    PROJECT_SLUG: str
    API_V1_STR: str

    ETL_HOST: str
    ETL_PORT: int
    ETL_SCHEMA: str

    REDIS_PORT: str
    REDIS_HOST: str

    REDIS_URI: Optional[RedisDsn] = None

    @validator("REDIS_URI", pre=True)
    def assembled_redis_uri(
            cls,
            v: Optional[str],
            values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_HOST"),
            port=values.get("REDIS_PORT"),
            path="/0"
        )

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()

