import datetime as dt

import flask

import connector


bp = flask.Blueprint("news", __name__, url_prefix="/news")

@bp.route("/links/", methods=[ "POST" ])
def createc_link():
    if not flask.request.is_json:
        return flask.abort(415, "Expected a JSON object.")

    link_in: dict = flask.request.get_json()

    try:
        print(f"{link_in['link']}", file=connector.get_links_file())
        return flask.jsonify()
    except Exception as e:
        print(f"[{dt.datetime.now().strftime('%H:%M - %d/%m/%Y')}] {link_in} {e.__class__} {e}", file=connector.get_log_file())
        return flask.abort(406)

