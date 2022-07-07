create_proposal_request = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "subject": {
            "type": "string",
            "description": "предмет закупки"
        },
        "segmet": {
            "type": "string",
            "description": "сегмент закупки"
        },
        "sub_segment": {
            "type": "string",
            "description": "подсегмент закупки"
        },
        "service_code": {
            "type": "string",
            "description": "код услуги"
        },
        "service_name": {
            "type": "string",
            "description": "наименование услуги"
        },
        "guaranteed_volume": {
            "type": "boolean",
            "description": "признак наличия гарантированного объема"
        }
    },
    "required": [
        "subject",
        "segmet",
        "sub_segment",
        "service_code",
        "service_name",
        "guaranteed_volume"
    ]
}

create_proposal_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "proposal_file": {
            "type": "string",
            "description": "Закодированный в base64 файл КП с макросами (в формате xlsm)"
        },
        "name": {
            "type": "string",
            "description": "имя файла"
        },
        "size": {
            "type": "integer",
            "description": "размер файла в байтах"
        }
    },
    "required": [
        "proposal_file",
        "name",
        "size"
    ]
}
