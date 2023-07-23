from pydantic import BaseSettings


class TestSettings(BaseSettings):
    es_host: str
    es_port: str
    es_schema: str

    redis_port: str
    redis_host: str

    es_index: str = Field('movies', env='ES_INDEX')
    es_id_field: str = Field('id', env='ES_ID_FIELD')

    service_url: str = 'http://movies_app_api/'
    auth_url: str = 'http://movies_app_auth/'

test_settings = TestSettings()
