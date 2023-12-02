import fastapi, pymongo, pydantic, bson

import qdrant_client as qdrant

from qdrant_client import models


class NewsEmbedding(pydantic.BaseModel):
    document_id: str
    representation: pydantic.conlist(float, min_length=768, max_length=768)

router = fastapi.APIRouter(prefix='/embeddings')

@router.get('/{document_id}')
def read(document_id: str, request: fastapi.Request):
    qdrant_client: qdrant.QdrantClient = request.app.state._QDRANT_CLIENT

    id = '-'.join([ "42069000", document_id[0:4], document_id[4:8], document_id[8:12], document_id[12:] ])

    try:
        response = qdrant_client.retrieve(collection_name="NewsEmbeddings", ids=[ id ], with_vectors=True)[0]
    except:
        raise fastapi.HTTPException(status_code=404, detail="Embedding not found for document.")

    return NewsEmbedding.model_validate(dict(document_id=document_id, representation=response.vector))

@router.post('/')
def create(d: NewsEmbedding, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT

    try:
        r = mongo.news.rawCollection.find_one(filter=dict(_id=bson.ObjectId(d.document_id)))

        if not r:
            raise Exception()
    except:
        raise fastapi.HTTPException(status_code=404, detail="Trying to create a representation for an inexistent document.")

    qdrant_client: qdrant.QdrantClient = request.app.state._QDRANT_CLIENT

    id = '-'.join([ "42069000", d.document_id[0:4], d.document_id[4:8], d.document_id[8:12], d.document_id[12:] ])

    qdrant_client.upsert(collection_name="NewsEmbeddings",
                         points=[ models.PointStruct(id=id, vector=d.representation) ])

    return dict(document_id=d.document_id)

@router.post('/similars/')
def find_similars(request: fastapi.Request,
                  vec: pydantic.conlist(float, min_length=768, max_length=768),
                  n: int = 5):
    qdrant_client: qdrant.QdrantClient = request.app.state._QDRANT_CLIENT

    similars = qdrant_client.search(collection_name="NewsEmbeddings", query_vector=vec, limit=n)

    qdrant_id_2_mongo_id = lambda qid: ''.join(qid.split('-')[1:])

    mongo_ids = [ qdrant_id_2_mongo_id(scored_point.id) for scored_point in similars ]

    return mongo_ids

