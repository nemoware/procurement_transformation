from collections import Counter

from openpyxl import load_workbook

from db.entity.lot import Lot
from db.entity.simple_entity import Segment, Sub_segment, Service, Stage, Unit, Rate
from itertools import groupby


def generate_prefilled_proposal(segment_name=None, sub_segment_name=None, service_code=None, service_name=None,
                                subject=None, guaranteed_volume=None):
    segment_name = 'Корпоратив защита и защита информации'
    sub_segment_name = '-'
    code = '90303'
    workbook = load_workbook(filename="Пустой шаблон.xlsm")
    sheet = workbook["Форма КП (для анализа рынка) ВР"]
    # sheet_reference_book = workbook["Справочник"]

    current_lots = (Lot.select(Lot, Segment, Sub_segment, Service, Stage, Rate, Unit)
                    .join(Segment).switch(Lot)
                    .join(Sub_segment).switch(Lot)
                    .join(Service).switch(Lot)
                    .join(Stage).switch(Lot)
                    .join(Rate).switch(Lot)
                    .join(Unit)
                    .where(Segment.name == segment_name, Sub_segment.name == sub_segment_name, Service.code == code))

    list_of_lots = []

    for lot in current_lots:
        list_of_lots.append({
            'number_of_stages': 0,
            'number_of_rates': 0,
            'id': lot.procurement_id,
            'service_code': lot.service_code.code,
            'stage_name': lot.stage_id.name,
            'rate_name': lot.rate_id.name,
            'unit_name': lot.unit_id.name,
            'is_null': lot.is_null,
            'segment_name': lot.segment_id.name,
            'sub_segment_name': lot.sub_segment_id.name,
        })
    list_of_lots = list(filter(lambda x: x['id'] != '0', list_of_lots))
    list_of_ids = list(set(map(lambda x: x['id'], list_of_lots)))
    list_of_ids.sort(key=lambda x: int(x[3:]))

    empty_list_of_ids = []
    empty_list_of_stages = []
    empty_list_of_rates = []
    empty_list_of_units = []
    number_of_stages = {}

    for lot in list_of_lots:
        if lot['id'] not in empty_list_of_ids or lot['stage_name'] not in empty_list_of_stages:
            empty_list_of_ids.append(lot['id'])
            empty_list_of_stages.append(lot['stage_name'])

            required_lot = [element for i, element in enumerate(list_of_lots) if
                            element['id'] in empty_list_of_ids and
                            element['stage_name'] == lot['stage_name']]
            required_lot.sort(key=lambda x: x['number_of_stages'], reverse=True)

            required_lot[0]['number_of_stages'] += 1
            for element in required_lot:
                element['number_of_stages'] = required_lot[0]['number_of_stages']

            # if number_of_stages.get(lot['stage_name'], False):
            #     number_of_stages[lot['stage_name']]['count'] += 1
            # else:
            #     number_of_stages[lot['stage_name']] = {
            #         'count': 1
            #     }

    list_of_lots.sort(key=lambda x: x['number_of_stages'], reverse=True)
    empty_list_of_stages = []

    for lot in list_of_lots:
        if next((item for item in empty_list_of_rates if
                 list(item.keys())[0] != lot['stage_name'] and list(item.values())[0] != lot['rate_name']), False):
            required_lot = [element for element in list_of_lots if
                            element['stage_name'] == lot['stage_name'] and
                            element['rate_name'] == lot['rate_name']]

            required_lot.sort(key=lambda x: x['number_of_stages'], reverse=True)
            required_lot[0]['number_of_rates'] += len(required_lot)

            for element in required_lot[1:]:
                element['number_of_rates'] = required_lot[0]['number_of_rates']

        obj = {}
        obj[lot['stage_name']] = lot['rate_name']
        # empty_list_of_stages.append(lot['stage_name'])
        empty_list_of_rates.append(obj)
        # empty_list_of_units.append(lot['unit_name'])

    number_of_stages = dict(reversed(sorted(number_of_stages.items(), key=lambda item: item[1]['count'], reverse=True)))
    i = len(number_of_stages)
    for stage in list(number_of_stages.keys()):
        if i == 7: break
        del number_of_stages[stage]
        i -= 1

    list_of_lots = list(filter(lambda x: number_of_stages.get(x['stage_name'], False), list_of_lots))
    list_of_lots.sort(key=lambda x: number_of_stages[x['stage_name']]['count'], reverse=True)

    number_of_rates = {}

    for stage_name in number_of_stages:
        for lot in list_of_lots:
            if lot['stage_name'] == stage_name:
                if not number_of_stages[stage_name].get(lot['rate_name'], False):
                    number_of_stages[stage_name][lot['rate_name']] = 1
                else:
                    number_of_stages[stage_name][lot['rate_name']] += 1

    print(123)
    # print(sheet['B18'].value)


def is_duplicate(lot, lot2) -> bool:
    return (lot2['is_null'] is not True and
            lot['is_null'] is not True and
            lot2['segment_name'] == lot['segment_name'] and
            lot2['sub_segment_name'] == lot['sub_segment_name'] and
            lot2['service_code'] == lot['service_code'])
