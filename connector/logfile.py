import os

import flask


def get_log_file():
    f = getattr(flask.g, "_APP_LOGFILE", None)

    if f is None:
        os.makedirs(".data", exist_ok=True)

        f = open(f".data/{os.getpid()}.log", "a")

        f = flask.g._APP_LOGFILE = f

    return f

