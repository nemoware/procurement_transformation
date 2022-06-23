import logging

from flask import Blueprint, jsonify, request

from api.common import validate_schema
from api.seeds_ranking import schemas
from api.seeds_ranking.seeds import generate_seeds, filter_asuz_data, filter_by_similarity

logger = logging.getLogger(__name__)
api = Blueprint('seeds_ranking', __name__)


@api.route('/api/seeds', methods=['POST'])
@validate_schema(schemas.seeds)
def get_seeds():
    zakupki_queries, marker_queries = generate_seeds(request.json['input_query'])
    return jsonify(dict(zakupki_gov_optimized=zakupki_queries, marker_interfax_optimized=marker_queries))


@api.route('/api/findlots', methods=['POST'])
@validate_schema(schemas.findlots)
def find_lots():
    return jsonify(filter_asuz_data(request.json))


@api.route('/api/calculate_similarity', methods=['POST'])
@validate_schema(schemas.calculate_similarity)
def calculate_similarity():
    subjects = filter_by_similarity(request.json['name_subject'], request.json['search_results'], 'name_objects')
    for subject in subjects:
        subject.pop('name_objects', None)
    return jsonify(subjects)
