from pydantic import BaseSettings


class Settings(BaseSettings):
    project_slug: str
    api_v1_str: str

    kafka_broker_url: str
    schema_registry_url: str
    number_partitions: int
    group_id: str

    ch_host: str
    ch_port: int
    ch_user: str
    ch_password: str
    ch_database: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
