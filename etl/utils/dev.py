from elasticsearch import Elasticsearch
from app.core.config import settings

es = Elasticsearch(
    [
        {
            "host": "loc",
            "port": settings.es_port,
            "scheme": settings.es_schema
        }
    ]
)