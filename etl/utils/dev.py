from app.core.config import settings
from elasticsearch import Elasticsearch

es = Elasticsearch(
    [{"host": "loc", "port": settings.es_port, "scheme": settings.es_schema}]
)
