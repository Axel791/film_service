from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field(default='elasticsearch', env='ES_HOST')
    es_port: int = Field(default=9200, env='ES_PORT')
    es_schema: str = Field(default='http', env='ES_SCHEMA')

    redis_port: int = Field(default=6379, env='REDIS_PORT')
    redis_host: str = Field(default='redis', env='REDIS_HOST')


test_settings = TestSettings()
