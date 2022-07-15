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

compare_proposal_from_initiator_request = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "proposal_file": {
            "type": "string",
            "description": "Закодированный в base64 файл КП без макросов (в формате xlsx)"
        },
        "procurement_id": {
            "type": "string",
            "description": "id закупки"
        }
    },
    "required": [
        "proposal_file",
        "procurement_id"
    ]
}

compare_proposal_from_initiator_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "enum": [
                            "subject",
                            "segment",
                            "sub_segment",
                            "service_code",
                            "service_name"
                        ],
                        "enumDesc": "поля из шапки КП",
                        "description": "лейбл поля из шапки КП"
                    },
                    "value": {
                        "type": "string",
                        "description": "значение поля из шапки КП"
                    },
                    "reference_book": {
                        "type": "boolean",
                        "description": "содержится ли поле в справочнике"
                    }
                },
                "required": [
                    "label",
                    "value",
                    "reference_book"
                ]
            },
            "description": "поля из шапки КП"
        },
        "stages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "наименование этапа"
                    },
                    "reference_book": {
                        "type": "boolean",
                        "description": "содержится ли этап в справочнике"
                    },
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "rate": {
                                    "type": "string",
                                    "description": "расценка"
                                },
                                "rate_reference_book": {
                                    "type": "boolean",
                                    "description": "содержится ли расценка в справочнике"
                                },
                                "unit": {
                                    "type": "string",
                                    "description": "единица измерения"
                                },
                                "unit_reference_book": {
                                    "type": "boolean",
                                    "description": "содержится ли единица измерения в справочнике"
                                }
                            },
                            "required": [
                                "unit",
                                "rate_reference_book",
                                "unit_reference_book",
                                "rate"
                            ]
                        },
                        "description": "строки таблицы"
                    }
                },
                "required": [
                    "name",
                    "reference_book",
                    "rows"
                ]
            },
            "description": "этапы из таблицы"
        }
    },
    "required": [
        "fields",
        "stages"
    ]
}
