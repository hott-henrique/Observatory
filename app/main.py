import contextlib, os

import fastapi
import pymongo, pymilvus

from app import news
from app import embeddings


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    app.state._MONGO_CLIENT = pymongo.MongoClient(username=os.getenv('JOURNALIST_USER'),
                                                  password=os.getenv('JOURNALIST_PWD'),
                                                  authSource='news')

    milvus_client = app.state._MILVUS_CLIENT = pymilvus.MilvusClient()

    milvus_db = pymilvus.Milvus()

    if not milvus_db.has_collection('embeddings'):
        fields = [
            pymilvus.FieldSchema(name='document_id', dtype=pymilvus.DataType.VARCHAR, is_primary=True, auto_id=False, max_length=128),
            pymilvus.FieldSchema(name='representation', dtype=pymilvus.DataType.FLOAT_VECTOR, dim=768)
        ]

        schema = pymilvus.CollectionSchema(fields=fields, description='Schema with 1:1 relation to documents in the news database.')

        milvus_client.create_collection_with_schema('embeddings', schema, index_params=None)

    yield

    app.state._MILVUS_CLIENT.close()

    app.state._MONGO_CLIENT.close()

app = fastapi.FastAPI(lifespan=lifespan)

app.include_router(news.router)
app.include_router(embeddings.router)
