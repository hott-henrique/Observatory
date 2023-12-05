import contextlib, os
import torch

import fastapi

import pymongo
import qdrant_client as qdrant

from app import news
from app import embeddings
from app import users


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    app.state._MONGO_CLIENT = pymongo.MongoClient(username=os.getenv('JOURNALIST_USER'),
                                                  password=os.getenv('JOURNALIST_PWD'),
                                                  authSource='news')

    app.state._QDRANT_CLIENT = qdrant.QdrantClient(url=os.getenv("QDRANT_URL"),
                                                   api_key=os.getenv("QDRANT_TOKEN"))
    
    yield

    app.state._QDRANT_CLIENT.close()

    app.state._MONGO_CLIENT.close()

app = fastapi.FastAPI(lifespan=lifespan)

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitações de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

app.include_router(news.router)
app.include_router(embeddings.router)
app.include_router(users.router)

