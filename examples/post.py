import datetime as dt

import requests


def post_document(doc: dict):
    if "title" not in doc:
        if type(doc["title"]) is not str:
            raise TypeError("The title must be an str.")
        raise KeyError("Missing the title key.")

    if "content" not in doc:
        if type(doc["content"]) is not str:
            raise TypeError("The content must be an str.")
        raise KeyError("Missing the content key.")

    if "author" not in doc:
        if type(doc["author"]) is not str:
            raise TypeError("The author must be an str.")
        raise KeyError("Missing the author key.")

    if "timestamp" not in doc:
        if type(doc["timestamp"]) is not float:
            raise TypeError("The timestamp must be an float.")
        raise KeyError("Missing the timestamp key.")

    if "categories" not in doc:
        if type(doc["categories"]) is not list:
            raise TypeError("The categories must be an list[str].")
        for category in doc["categories"]:
            if type(category) is not str:
                raise TypeError("Each category must be an str.")
        raise KeyError("Missing the categories key.")

    if "link" not in doc:
        if type(doc["link"]) is not str:
            raise TypeError()
        raise KeyError("Missing the link key.")

    doc = dict(title=doc["title"],
               content=doc["content"],
               author=doc["author"],
               timestamp=doc["timestamp"],
               categories=doc["categories"],
               link=doc["link"])

    resp = requests.post(url="http://127.0.0.1:5000/api/news/", json=doc)

    if not resp.ok:
        raise RuntimeError()

    return resp.json()

moment = dt.datetime.now()

news = dict(title="Title",
            content="Content",
            author="Author",
            timestamp=moment.timestamp(),
            categories=[ "A", "B" ],
            link="https://www.google.com/")

print(post_document(doc=news))

