import datetime as dt
import os

import requests


def post_document(doc: dict):
    if "title" not in doc:
        raise KeyError("Missing the title key.")

    if type(doc["title"]) is not str:
        raise TypeError("The title must be an str.")

    if "content" not in doc:
        raise KeyError("Missing the content key.")

    if type(doc["content"]) is not str:
        raise TypeError("The content must be an str.")

    if "authors" not in doc:
        raise KeyError("Missing the authors key.")

    if type(doc["authors"]) is not list:
        for author in doc["authors"]:
            if type(author) is not str:
                raise TypeError("Each author must be an str.")
        raise TypeError("The authors must be an list[str].")

    if "timestamp" not in doc:
        raise KeyError("Missing the timestamp key.")

    if type(doc["timestamp"]) is not float:
        raise TypeError("The timestamp must be an float.")

    if "categories" not in doc:
        if type(doc["categories"]) is not list:
            raise TypeError("The categories must be an list[str].")

        for category in doc["categories"]:
            if type(category) is not str:
                raise TypeError("Each category must be an str.")

        raise KeyError("Missing the categories key.")

    if "link" not in doc:
        raise KeyError("Missing the link key.")

    if type(doc["link"]) is not str:
        raise TypeError()

    doc = dict(title=doc["title"],
               content=doc["content"],
               authors=doc["authors"],
               timestamp=doc["timestamp"],
               categories=doc["categories"],
               link=doc["link"])

    resp = requests.post(url=f"{os.getenv('API_BASE_URL')}/api/news/", json=doc)

    if not resp.ok:
        raise RuntimeError(f"Failed to post doc: {doc}")

    return resp.json()

moment = dt.datetime.now()

news = dict(title="Title",
            content="Content",
            author="Author",
            timestamp=moment.timestamp(),
            categories=[ "A", "B" ],
            link="localhost")

print(f"Document posted with success: {post_document(doc=news)}")

