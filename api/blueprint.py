import flask

from api import news, links


bp = flask.Blueprint("api", __name__, url_prefix="/api")

bp.register_blueprint(news.bp)
bp.register_blueprint(links.bp)

