import logging

import jsonschema
from flask import Blueprint, request, jsonify

from api.common import validate_schema
from api.proposal_reference_book import schemas
from api.proposal_reference_book.analysis import compare_proposal
from api.proposal_reference_book.generator import generate_prefilled_proposal

logger = logging.getLogger(__name__)
api = Blueprint('proposal', __name__)


@api.route('/api/create_proposal', methods=['POST'])
@validate_schema(schemas.create_proposal_request)
def get_proposal():
    try:
        subject = request.json['subject']
        segment = request.json['segmet']
        sub_segment = request.json['sub_segment']
        service_code = request.json['service_code']
        service_name = request.json['service_name']
        guaranteed_volume = request.json['guaranteed_volume']

        response_data = generate_prefilled_proposal(
            segment_name=segment,
            service_code=service_code,
            sub_segment_name=sub_segment,
            subject=subject,
            service_name=service_name,
            guaranteed_volume=guaranteed_volume
        )

        jsonschema.validate(response_data, schemas.create_proposal_response)
        return jsonify(response_data)
    except jsonschema.exceptions.ValidationError as err:
        logger.exception(err.message)
        raise Exception(err.message)
    except Exception as e:
        logger.exception(e)
        raise


@api.route('/api/compare_proposal_from_initiator', methods=['POST'])
@validate_schema(schemas.compare_proposal_from_initiator_request)
def compare_proposal_from_initiator():
    try:
        proposal_file = request.json['proposal_file']
        procurement_id = request.json['procurement_id']

        response_data = compare_proposal(proposal_file, procurement_id)
        jsonschema.validate(response_data, schemas.compare_proposal_from_initiator_response)
        return jsonify(response_data)
    except jsonschema.exceptions.ValidationError as err:
        logger.exception(err.message, exc_info=False)
        raise Exception(err.message)
    except Exception as e:
        logger.exception(e)
        raise
