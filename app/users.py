import fastapi
import pydantic
import pymongo
import bson
import qdrant_client as qdrant
import numpy as np
import typing as t
import datetime

class User(pydantic.BaseModel):
    name: str
    history: t.Optional[list[str]] = list()
    password: str

class News(pydantic.BaseModel):
    title: str
    authors: list[str]
    content: str
    timestamp: float
    categories: list[str]
    link: str

router = fastapi.APIRouter(prefix='/users')

@router.post('/')
def create(u: User, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.usersLog.insert_one(dict(u))
    return { 'user_id': str(r.inserted_id) }

@router.get('/')
def read(name: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.usersLog.find_one(filter={ "name":  name })

    if r is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found.")

    return User.model_validate(r)

@router.delete('/')
def delete(name: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.usersLog.delete_one({ "name":  name })
    return { 'deleted': r.deleted_count }

@router.post('/{name}/read/{item_id}')
def update(name: str, item_id: str, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    r = mongo.news.usersLog.update_one(filter= { "name":  name },\
                                            update= {'$push': {'history': item_id}})

    if not r.modified_count:
        raise fastapi.HTTPException(status_code=404, detail="User not found.")

    return r.modified_count

@router.get('/{name}/recommender/{n}')
def recommender(name: str, n: int, request: fastapi.Request):

    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    qdrant_client: qdrant.QdrantClient = request.app.state._QDRANT_CLIENT

    r = mongo.news.usersLog.find_one(filter= { "name":  name })
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
        if "undefined" in str(document_id)
    ]

    response = qdrant_client.retrieve(collection_name="NewsEmbeddings", ids=qdrant_ids, with_vectors=True)
    vec = np.array([np.array(v.vector) for v in response])
    user_vec = vec.mean(axis=0)
    similars_points = qdrant_client.search(collection_name="NewsEmbeddings", query_vector=user_vec, limit=50)

    qdrant_id_2_mongo_id = lambda qid: ''.join(qid.split('-')[1:])

    mongo_ids = [ qdrant_id_2_mongo_id(scored_point.id) for scored_point in similars_points 
                 if qdrant_id_2_mongo_id(scored_point.id) not in u.history][:n]

    rec_news = [
        mongo.news.rawCollection.find_one(filter={ "_id":  bson.ObjectId(document_id) })
        for document_id in mongo_ids 
    ]

    recommendations = list()

    for n in rec_news:
        n['_id'] = str(n['_id'])
        if isinstance(n['timestamp'], str) and '-' in n['timestamp']:
            continue
        recommendations.append(n)

    recommendations.sort(key=lambda news: float(news['timestamp']), reverse=True)
    for news in recommendations:
        news['timestamp'] = str(datetime.datetime.utcfromtimestamp(news['timestamp']).strftime('%d-%m-%Y'))

    return recommendations