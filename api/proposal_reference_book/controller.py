import logging

import jsonschema
from flask import Blueprint, request

from api.common import validate_schema
from api.proposal_reference_book import schemas

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



        jsonschema.validate(None, schemas.create_proposal_response)
    except jsonschema.exceptions.ValidationError as err:
        logger.exception(err)
    except Exception as e:
        logger.exception(e)
        raise
