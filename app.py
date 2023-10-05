import flask

import api


def create_app():
    app = flask.Flask(__name__)

    app.register_blueprint(api.bp)

    @app.teardown_appcontext
    def close_connection(_):
        f = getattr(flask.g, "_APP_LOGFILE", None)

        if f is not None:
            f.close()

        f = getattr(flask.g, "_APP_LINKSFILE", None)

        if f is not None:
            f.close()

        db = getattr(flask.g, "_MONGODB_INSTANCE", None)

        if db is not None:
            db.close()

    return app

