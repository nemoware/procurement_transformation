import logging
import time

from flask import Blueprint, jsonify, request

from api.common import validate_schema
from api.seeds_ranking import schemas
from api.seeds_ranking.seeds import generate_seeds, filter_asuz_data, filter_by_similarity

logger = logging.getLogger(__name__)
api = Blueprint('seeds_ranking', __name__)


@api.route('/api/seeds', methods=['POST'])
@validate_schema(schemas.seeds)
def get_seeds():
    try:
        logger.info('Start seed queries generation')
        start = time.perf_counter()
        zakupki_queries, marker_queries = generate_seeds(request.json['input_query'])
        logger.info(f'End seed queries generation. Time spent={round(time.perf_counter() - start, 2)}s')
        return jsonify(dict(zakupki_gov_optimized=zakupki_queries, marker_interfax_optimized=marker_queries))
    except Exception as e:
        logger.exception(e)
        raise


@api.route('/api/findlots', methods=['POST'])
@validate_schema(schemas.findlots)
def find_lots():
    try:
        logger.info('Start find_lots')
        start = time.perf_counter()
        result = filter_asuz_data(request.json)
        logger.info(f'End find_lots. Time spent={round(time.perf_counter() - start, 2)}s')
        return jsonify(result)
    except Exception as e:
        logger.exception(e)
        raise


@api.route('/api/calculate_similarity', methods=['POST'])
@validate_schema(schemas.calculate_similarity)
def calculate_similarity():
    try:
        logger.info('Start calculate_similarity')
        start = time.perf_counter()
        subjects = filter_by_similarity(request.json['name_subject'], request.json['search_results'], 'name_objects')
        for subject in subjects:
            subject.pop('name_objects', None)
        logger.info(f'End calculate_similarity. Time spent={round(time.perf_counter() - start, 2)}s')
        return jsonify(subjects)
    except Exception as e:
        logger.exception(e)
        raise
