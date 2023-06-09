from typing import Any, Dict, Optional
from pydantic import BaseSettings, RedisDsn, validator


class Settings(BaseSettings):
    PROJECT_SLUG: str = 'movies_app'
    API_V1_STR: str = '/api/v1'

    ETL_HOST: str = '127.0.0.1'
    ETL_PORT: int = 9200
    ETL_SCHEMA: str = 'http'

    REDIS_PORT: str = 6379
    REDIS_HOST: str = '127.0.0.1'

    REDIS_URI: Optional[RedisDsn] = None
    FILM_CACHE_EXPIRE_IN_SECOND: int = 60

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

