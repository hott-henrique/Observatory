import flask

from api import news


bp = flask.Blueprint("api", __name__, url_prefix="/api")

bp.register_blueprint(news.bp)

