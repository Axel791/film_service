from elasticsearch import Elasticsearch

es = Elasticsearch(
    [
        {
            "host": "loc",
            "port": settings.ETL_PORT,
            "scheme": settings.ETL_SCHEMA
        }
    ]
)