import fastapi
import pydantic
import pymongo
import bson
import qdrant_client as qdrant
import numpy as np

from news import News

class User(pydantic.BaseModel):
    name: str
    history: list[str]

router = fastapi.APIRouter(prefix='/users')

@router.post('/')
def create(u: User, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.usersLog.insert_one(dict(u))
    return { 'user_id': str(u.inserted_id) }

@router.get('/{user_id}')
def read(user_id: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.usersLog.find_one(filter={ "_id":  bson.ObjectId(user_id) })

    if r is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found.")

    return User.model_validate(r)

@router.delete('/{user_id}')
def delete(user_id: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.usersLog.delete_one({ "_id":  bson.ObjectId(user_id) })
    return { 'deleted': r.deleted_count }

@router.post('/{user_id}/read/{item_id}')
def update(user_id: str, item_id: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.usersLog.update_one(filter= { "_id":  bson.ObjectId(user_id) },\
                                            update= {'$push': {'history': item_id}})

    if not r.modified_count:
        raise fastapi.HTTPException(status_code=404, detail="User not found.")

    return r.modified_count

@router.get('/{user_id}/recommender/{n}')
def recommender(user_id: str, n: str, request: fastapi.Request):

    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    qdrant_client: qdrant.QdrantClient = request.app.state._QDRANT_CLIENT

    r = mongo.news.usersLog.find_one(filter= { "_id":  bson.ObjectId(user_id) })
    if r is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found.")
    
    u = User.model_validate(r)
    
    if len(u.history) < 1:
        categories = ["football", "basketball", "futebol americano", "baseball"]
        news_by_category = list()
        for cat in categories:
            result = mongo.news.rawCollection.aggregate([
                {"$match": {"categories": {"$in": [cat]}}}, 
                {"$sample": {"size": int(n)}}
            ])
        news_by_category.extend(result)
        return news_by_category

    qdrant_ids = [
        '-'.join([ "42069000", document_id[0:4], document_id[4:8], document_id[8:12], document_id[12:] ])
        for document_id in u.history
    ]
    response = qdrant_client.retrieve(collection_name="NewsEmbeddings", ids=qdrant_ids, with_vectors=True)
    vec = np.array([np.array(v.vector) for v in response])
    user_vec = vec.mean(axis=0)
    similars = qdrant_client.search(collection_name="NewsEmbeddings", query_vector=user_vec, limit=50)

    qdrant_id_2_mongo_id = lambda qid: ''.join(qid.split('-')[1:])

    mongo_ids = [ qdrant_id_2_mongo_id(scored_point.id) for scored_point in similars 
                 if qdrant_id_2_mongo_id(scored_point.id) not in u.history][:n]

    rec_news = {
        News.model_validate(
            mongo.news.rawCollection.find_one(filter={ "_id":  bson.ObjectId(document_id) })
        )
        for document_id in mongo_ids 
    }

    return rec_news