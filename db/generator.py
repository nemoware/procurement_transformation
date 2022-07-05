from collections import Counter

from openpyxl import load_workbook

from db.entity.lot import Lot
from db.entity.simple_entity import Segment, Sub_segment, Service, Stage, Unit, Rate
from itertools import groupby


def generate_():
    segment_name = 'Разраб/Поддерж IT СистемИОборудования'
    sub_segment_name = '-'
    code = '11272'
    workbook = load_workbook(filename="Пустой шаблон.xlsm")
    sheet = workbook["Форма КП (для анализа рынка) ВР"]
    sheet_reference_book = workbook["Справочник"]

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
            # 'id': lot.procurement_id,
            'segment_name': lot.segment_id.name,
            'sub_segment_name': lot.sub_segment_id.name,
            'service_code': lot.service_code.code,
            'stage_name': lot.stage_id.name,
            'rate_name': lot.rate_id.name,
            'unit_name': lot.unit_id.name,
            'is_null': lot.is_null
        })

    # most_common_lots_by_stage_name: list[tuple[str, int]] = [
    #     i for i in Counter(lot['stage_name'] for lot in list_of_lots).most_common(10)
    # ]
    # second_list_of_lots = []
    # for common in most_common_lots_by_stage_name:
    #     second_list_of_lots.extend([x for x in list_of_lots if x['stage_name'] == common[0]])
    #
    # most_common_lots_by_rate_name = [i for i in
    #                                  Counter(lot['rate_name'] for lot in second_list_of_lots).most_common(20)]
    # list_of_lots = []
    # for common in most_common_lots_by_rate_name:
    #     list_of_lots.extend([x for x in second_list_of_lots if x['rate_name'] == common[0]])
    #
    # most_common_lots_by_unit_name = [i for i in Counter(lot['unit_name'] for lot in list_of_lots).most_common()]
    # second_list_of_lots = []
    # for common in most_common_lots_by_unit_name:
    #     second_list_of_lots.extend([x for x in list_of_lots if x['unit_name'] == common[0]])
    #
    # result_for_reference_book = []
    # for key, group_items in groupby(sorted(second_list_of_lots, key=lambda x: x['stage_name']),
    #                                 lambda x: x['stage_name']):
    #     update_lot = list(group_items)[0]
    #     result_for_reference_book.append({'count': len(list(group_items)), **update_lot})

    for lot in list_of_lots:
        lot['number_of_stages'] = sum(1 for j in list_of_lots if
                                      j['stage_name'] == lot['stage_name'] and
                                      is_duplicate(j, lot))
        lot['number_of_rates'] = sum(1 for j in list_of_lots if
                                     j['rate_name'] == lot['rate_name'] and
                                     j['stage_name'] == lot['stage_name'] and
                                     is_duplicate(j, lot))
        lot['number_of_units'] = sum(1 for j in list_of_lots if
                                     j['unit_name'] == lot['unit_name'] and
                                     j['stage_name'] == lot['stage_name'] and
                                     j['rate_name'] == lot['rate_name'] and
                                     is_duplicate(j, lot))

    # list_of_lots = list(filter(lambda x: x['is_null'] is not True, list_of_lots))

    print(sheet['B18'].value)


def is_duplicate(lot, lot2) -> bool:
    return (lot2['is_null'] is not True and
            lot['is_null'] is not True and
            lot2['segment_name'] == lot['segment_name'] and
            lot2['sub_segment_name'] == lot['sub_segment_name'] and
            lot2['service_code'] == lot['service_code'])
