import fastapi
import pydantic
import pymongo
import bson
import datetime
import requests

import qdrant_client as qdrant

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
def rand_news_from_each_category(n: int, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT
    categories = ["football", "basketball", "futebol americano", "baseball"]
    news_by_category = list()
    for cat in categories:
        result = mongo.news.rawCollection.aggregate([
            {"$match": {"categories": {"$in": [cat]}}}, 
            {"$sample": {"size": int(n) * 10}}
        ])

        for news in list(result):
            if '-' in news['timestamp']:
                continue
            news['_id'] = str(news['_id'])
            news_by_category.append(news)

        news_by_category.sort(key=lambda news: float(news['timestamp']))

        for news in news_by_category:
            news['timestamp'] = str(datetime.datetime.utcfromtimestamp(news['timestamp']).strftime('%d-%m-%Y'))

    return news_by_category[:n]


@router.get('/recents/{n}')
def most_recent_news(n: int, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT

    full_news = list()
     
    result = mongo.news.rawCollection.find().sort(
        "timestamp", -1
    )

    for news in list(result[:n]):
        news['_id'] = str(news['_id'])
        news['timestamp'] = str(datetime.datetime.utcfromtimestamp(news['timestamp']).strftime('%d-%m-%Y'))
        full_news.append(news)

    return full_news

@router.get('/recents/{category}/{n}')
def most_recent_by_category(category: str, n: int, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT

    full_news = list()

    if category not in ["football", "basketball", "futebol americano", "baseball"]:
        return {}
     
    result = mongo.news.rawCollection.find(
        {"categories": category}
    ).sort(
        "timestamp", -1
    )

    for news in list(result[:n]):
        news['_id'] = str(news['_id'])
        news['timestamp'] = str(datetime.datetime.utcfromtimestamp(news['timestamp']).strftime('%d-%m-%Y'))
        full_news.append(news)

    return full_news


@router.get('/search/')
def search_query(q: str, n: int, request: fastapi.Request):
    mongo: pymongo.MongoClient = request.app.state._MONGO_CLIENT

    qdrant_client: qdrant.QdrantClient = request.app.state._QDRANT_CLIENT

    response = requests.get("http://172.18.0.216:8080/news/search/", params=dict(q=q))

    response_obj = response.json()

    vector = response_obj['embeddings']

    similars = qdrant_client.search(collection_name="NewsEmbeddings", query_vector=vector, limit=n)

    qdrant_id_2_mongo_id = lambda qid: ''.join(qid.split('-')[1:])

    mongo_ids = [ qdrant_id_2_mongo_id(scored_point.id) for scored_point in similars ]

    news = [ mongo.news.rawCollection.find_one(filter={ "_id":  bson.ObjectId(document_id) }) for document_id in mongo_ids ]

    valid_news = list()
    for n in news:
        n['_id'] = str(n['_id'])
        valid_news.append(News.model_validate(n))

    return valid_news