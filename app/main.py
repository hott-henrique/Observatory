import contextlib, os
import torch

import fastapi

import pymongo
import qdrant_client as qdrant

from app import news
from app import embeddings


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    app.state._MONGO_CLIENT = pymongo.MongoClient(username=os.getenv('JOURNALIST_USER'),
                                                  password=os.getenv('JOURNALIST_PWD'),
                                                  authSource='news')

    app.state._QDRANT_CLIENT = qdrant.QdrantClient(url=os.getenv("QDRANT_URL"),
                                                   api_key=os.getenv("QDRANT_TOKEN"))
    
    try:
        app.state._BERT_MODEL = torch.load("path/to/model", map_location=torch.device('cpu'))
    except:
        pass


    yield

    app.state._QDRANT_CLIENT.close()

    app.state._MONGO_CLIENT.close()

app = fastapi.FastAPI(lifespan=lifespan)

app.include_router(news.router)
app.include_router(embeddings.router)

