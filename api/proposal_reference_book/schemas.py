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

compare_proposal_from_counterparty_request = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "original_proposal": {
            "type": "string",
            "description": "Оригинальный закодированный в base64 файл КП (в формате xlsx)"
        },
        "proposal_from_counterparty": {
            "type": "string",
            "description": "Присланный контрагентом закодированный в base64 файл КП (в формате xlsx)"
        }
    },
    "required": [
        "original_proposal",
        "proposal_from_counterparty"
    ]
}
compare_proposal_from_counterparty_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "structure": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "element": {
                        "type": "string",
                        "enum": [
                            "field",
                            "column"
                        ],
                        "description": "измененный структурный элемент"
                    },
                    "change_type": {
                        "type": "string",
                        "enum": [
                            "+",
                            "-"
                        ],
                        "description": "добавление или удаление"
                    },
                    "name": {
                        "type": "string",
                        "description": "имя элемента"
                    }
                },
                "required": [
                    "element",
                    "change_type",
                    "name"
                ]
            },
            "description": "изменения структуры"
        },
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
                            "service_name",
                            "counterparty_name",
                            "currency",
                            "term"
                        ],
                        "enumDesc": "поля из шапки КП",
                        "description": "лейбл поля из шапки КП"
                    },
                    "value": {
                        "type": "string",
                        "description": "значение поля из шапки КП"
                    },
                    "original_value": {
                        "type": "string",
                        "description": "значение поля из шапки оригинального КП, если значение было изменено"
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
                    "synonym": {
                        "type": "string",
                        "description": "возможный синоним, если этап отсутствует в справочнике"
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
                                "rate_synonym": {
                                    "type": "string",
                                    "description": "возможный синоним расценки, если расценка не содержится в справочнике"
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
                                },
                                "change_type": {
                                    "type": "string",
                                    "enum": [
                                        "+",
                                        "-"
                                    ],
                                    "description": "добавление или удаление"
                                },
                                "values": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "label": {
                                                "type": "string",
                                                "description": "наименование столбца в таблице"
                                            },
                                            "value": {
                                                "type": "string",
                                                "description": "значение ячейки"
                                            }
                                        },
                                        "required": [
                                            "label",
                                            "value"
                                        ]
                                    },
                                    "description": "все остальные значения, кроме этапа, расценки и единицы измерения"
                                }
                            },
                            "required": [
                                "unit",
                                "values",
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
        },
        "travel_expenses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "наименование столбца"
                    },
                    "value": {
                        "type": "string",
                        "description": "значение ячейки"
                    }
                },
                "required": [
                    "label",
                    "value"
                ]
            },
            "description": "командировочные расходы"
        },
        "vat": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "наименование столбца"
                    },
                    "value": {
                        "type": "string",
                        "description": "значение ячейки"
                    }
                },
                "required": [
                    "label",
                    "value"
                ]
            },
            "description": "сумма НДС"
        }
    },
    "required": [
        "structure",
        "fields",
        "stages",
        "vat"
    ]
}
