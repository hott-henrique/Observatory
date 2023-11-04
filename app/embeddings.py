import fastapi, pymongo, pymilvus, pydantic, bson


class NewsEmbedding(pydantic.BaseModel):
    document_id: str
    representation: pydantic.conlist(float, min_length=768, max_length=768)

router = fastapi.APIRouter(prefix='/embeddings')

@router.get('/{document_id}')
def read(document_id: str, request: fastapi.Request):
    milvus: pymilvus.MilvusClient = request.app.state._MILVUS_CLIENT

    r = milvus.query('embeddings', filter=f'document_id == "{document_id}"')

    if not r:
        raise fastapi.HTTPException(status_code=404, detail="Embedding not found for document.")

    return NewsEmbedding.model_validate(r.pop())

@router.post('/')
def create(d: NewsEmbedding, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT

    try:
        r = mongo.news.rawCollection.find_one(filter=dict(_id=bson.ObjectId(d.document_id)))

        if not r:
            raise Exception()
    except:
        raise fastapi.HTTPException(status_code=404, detail="Trying to create an representation for an inexistent document.")

    milvus: pymilvus.MilvusClient = request.app.state._MILVUS_CLIENT

    r = milvus.query('embeddings', filter=f'document_id == "{d.document_id}"')

    if r:
        raise fastapi.HTTPException(status_code=409, detail="Trying to overwrite an document representation..")

    r = milvus.insert('embeddings', [ dict(document_id=d.document_id, representation=d.representation) ])

    milvus.flush('embeddings')

    return dict(document_id=r.pop())
