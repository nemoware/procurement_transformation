seeds = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "input_query": {
            "type": "string",
            "description": "Исходный запрос, по которому будут сгенерированы seed-запросы"
        }
    },
    "required": [
        "input_query"
    ]
}

findlots = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "search_request": {
            "type": "string",
            "description": "исходный поисковый запрос"
        },
        "usl_code": {
            "type": ["array", "null"],
            "items": {
                "type": "string"
            },
            "description": "код КТ-777"
        },
        "usl_name": {
            "type": ["string", "null"],
            "description": "наименование услуги КТ-777"
        },
        "start_pur_date": {
            "type": ["string", "null"],
            "description": "начало диапазона дат закупки",
            "format": "date"
        },
        "finish_pur_date": {
            "type": ["string", "null"],
            "description": "конец диапазона дат закупки",
            "format": "date"
        }
    },
    "required": [
        "search_request"
    ]
}

calculate_similarity = {
    "type": "object",
    "properties": {
        "name_subject": {
            "type": "string",
            "description": "исходный запрос"
        },
        "search_results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "id закупки"
                    },
                    "name_objects": {
                        "type": "string",
                        "description": "предмет закупки"
                    }
                },
                "required": [
                    "id",
                    "name_objects"
                ]
            },
            "minItems": 1,
            "description": "предметы закупок"
        }
    },
    "required": [
        "name_subject",
        "search_results"
    ]
}
