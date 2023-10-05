import os

import flask


def get_log_file():
    f = getattr(flask.g, "_APP_LOGFILE", None)

    if f is None:
        os.makedirs(".STORAGE", exist_ok=True)

        f = open(f".STORAGE/{os.getpid()}.log", "a")

        f = flask.g._APP_LOGFILE = f

    return f

def get_links_file():
    f = getattr(flask.g, "_APP_LINKSFILE", None)

    if f is None:
        os.makedirs(".STORAGE", exist_ok=True)

        f = open(f".STORAGE/{os.getpid()}.links", "a")

        f = flask.g._APP_LOGFILE = f

    return f


