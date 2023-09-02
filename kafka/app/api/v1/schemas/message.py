from app.api.v1.schemas.orjson_dump import BaseOrjson


class Message(BaseOrjson):
    message: dict
