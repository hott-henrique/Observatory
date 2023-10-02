import os

import flask, pymongo


def get_news_db():
    db = getattr(flask.g, "_MONGODB_INSTANCE", None)

    if db is None:
        user = os.getenv('JOURNALIST_USER')
        pwd = os.getenv('JOURNALIST_PWD')

        client = pymongo.MongoClient(username=user,
                                     password=pwd,
                                     authSource="news")

        db = flask.g._MONGODB_INSTANCE = client

    return db.news

