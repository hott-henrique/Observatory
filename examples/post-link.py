import os

import requests


def post_link(link: dict):
    if "link" not in link:
        raise KeyError("Missing the link key.")

    if type(link["link"]) is not str:
        raise TypeError("The link must be an str.")

    resp = requests.post(url=f"{os.getenv('API_BASE_URL')}/api/links/", json=link)

    if not resp.ok:
        raise RuntimeError(f"Failed to post link: {link}")

    return resp.json()

link = dict(link="www.google.com")

print(f"Link posted with success: {post_link(link=link)}")

