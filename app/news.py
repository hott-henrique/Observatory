import fastapi
import pydantic
import pymongo
import bson


class News(pydantic.BaseModel):
    title: str
    authors: list[str]
    content: str
    timestamp: float
    categories: list[str]
    link: str

router = fastapi.APIRouter(prefix='/news')

@router.post('/')
def create(n: News, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.rawCollection.insert_one(dict(n))
    return { 'document_id': str(r.inserted_id) }

@router.get('/{document_id}')
def read(document_id: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.rawCollection.find_one(filter={ "_id":  bson.ObjectId(document_id) })

    if r is None:
        raise fastapi.HTTPException(status_code=404, detail="Document not found.")

    return News.model_validate(r)

@router.delete('/{document_id}')
def delete(document_id: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.rawCollection.delete_one({ "_id":  bson.ObjectId(document_id) })
    return { 'deleted': r.deleted_count }

@router.get('/randnews/{n}')
def rand_news_from_each_category(n: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    categories = ["football", "basketball", "futebol americano", "baseball"]
    news_by_category = list()
    for cat in categories:
        result = mongo.news.rawCollection.aggregate([
            {"$match": {"categories": {"$in": [cat]}}}, 
            {"$sample": {"size": int(n)}}
        ])
        news_by_category.extend(result)

    return news_by_category
