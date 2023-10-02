import os

import flask

import api


def create_app():
    os.makedirs(".STORAGE", exist_ok=True)

    app = flask.Flask(__name__)

    app.register_blueprint(api.bp)

    return app

