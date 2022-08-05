import logging

import flask
from flask import jsonify

from api.common import env_var
from api.seeds_ranking.routes import api as seeds_ranking_api
from api.proposal_reference_book.controller import api as proposal_reference_book_api
from db import db_init

logging.basicConfig(level=logging.INFO, force=True)
__version__ = "1.0.0"
logger = logging.getLogger(__name__)


def default_error_handler(error):
    return {'message': str(error), 'version': __version__}, getattr(error, 'code', 500)


def get_status():
    return jsonify(dict(message='ok', version=__version__))


def create_app():
    app = flask.Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.register_blueprint(seeds_ranking_api)
    app.register_blueprint(proposal_reference_book_api)
    app.register_error_handler(Exception, default_error_handler)
    app.add_url_rule('/api/status', view_func=get_status, methods=['GET'])
    return app


if __name__ == "__main__":
    if db_init.create_table():
        port = env_var('PROCUREMENT_SERVICE_PORT', 5001)
        create_app().run(host='0.0.0.0', port=port)
