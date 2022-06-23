import datetime
import logging
import os
from functools import wraps

import jsonschema
from flask import request, jsonify
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)


def validate_schema(schema):
    validator = Draft7Validator(schema, format_checker=jsonschema.FormatChecker())

    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            input = request.get_json(force=True)
            errors = [error.message for error in validator.iter_errors(input)]
            if errors:
                logger.error(errors)
                response = jsonify(dict(message="invalid input", errors=errors))
                response.status_code = 400
                return response
            else:
                return fn(*args, **kwargs)
        return wrapped
    return wrapper


def env_var(vname, default_val=None):
    if vname not in os.environ:
        msg = f'define {vname} environment variable! defaulting to {default_val}'
        logger.warning(msg)
        return default_val
    else:
        return os.environ[vname]


def json_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    # elif isinstance(x, bson.objectid.ObjectId):
    #     return str(x)
