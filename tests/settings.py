from pydantic import BaseSettings


class TestSettings(BaseSettings):
    es_host: str
    es_port: str
    es_schema: str

    redis_port: str
    redis_host: str



test_settings = TestSettings()
