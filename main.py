import argparse
import logging

import flask
from werkzeug.exceptions import HTTPException

from api.seeds_ranking.routes import api as seeds_ranking_api
from api.common import env_var

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
__version__ = "1.0.0"
logger = logging.getLogger(__name__)


def default_error_handler(error):
    return {'message': str(error), 'version': __version__}, getattr(error, 'code', 500)


def create_app():
    app = flask.Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.register_blueprint(seeds_ranking_api)
    app.register_error_handler(Exception, default_error_handler)
    return app


if __name__ == "__main__":
    port = env_var('PROCUREMENT_SERVICE_PORT', 5001)
    create_app().run(host='0.0.0.0', port=port)
