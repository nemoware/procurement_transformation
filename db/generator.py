from collections import Counter

from openpyxl import load_workbook
from peewee import JOIN
from playhouse.shortcuts import model_to_dict

from db.entity.lot import Lot
from db.entity.simple_entity import Segment, Sub_segment, Service, Stage, Unit, Rate


def generate_():
    segment_name = 'Консалтинг'
    sub_segment_name = 'Аналитические исследования'
    code = '91202'
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
    tree_of_lots = {
        'segment_name': segment_name,
        'sub_segment_name': sub_segment_name,
        'service_code': code,
        'stage': []
    }

    for lot in current_lots:
        list_of_lots.append({
            'id': lot.procurement_id,
            'segment_name': lot.segment_id.name,
            'sub_segment_name': lot.sub_segment_id.name,
            'service_code': lot.service_code.code,
            'stage_name': lot.stage_id.name,
            'rate_name': lot.rate_id.name,
            'unit_name': lot.unit_id.name,
        })

        stage_index = next(
            (index for index, d in enumerate(tree_of_lots['stage']) if d["stage_name"] == lot.stage_id.name),
            None
        )
        if stage_index is None:
            tree_of_lots['stage'].append({
                'stage_name': lot.stage_id.name,
                'rates': [],
                'count': 0
            })
            stage_index = -1
        else:
            tree_of_lots['stage'][stage_index]['count'] += 1

        rate_index = next(
            (index for index, d in enumerate(tree_of_lots['stage'][stage_index]['rates']) if
             d["rate_name"] == lot.rate_id.name),
            None
        )
        if rate_index is None:
            tree_of_lots['stage'][stage_index]['rates'].append({
                'rate_name': lot.rate_id.name,
                'units': [],
                'count': 0
            })
            rate_index = -1
        else:
            tree_of_lots['stage'][stage_index]['rates'][rate_index]["count"] += 1

        unit_index = next(
            (index for index, d in enumerate(tree_of_lots['stage'][stage_index]['rates'][rate_index]["units"])
             if d["unit_name"] == lot.unit_id.name),
            None
        )
        if unit_index is not None:
            tree_of_lots['stage'][stage_index]['rates'][rate_index]["units"][unit_index]['count'] += 1
            tree_of_lots['stage'][stage_index]['rates'][rate_index]["units"][unit_index]['ids'].append(
                lot.procurement_id)
        else:
            tree_of_lots['stage'][stage_index]['rates'][rate_index]["units"].append({
                'unit_name': lot.unit_id.name,
                'ids': [lot.procurement_id],
                'count': 0
            })

        # if not tree_of_lots['stage'][lot.stage_id.name].get(lot.rate_id.name):
        #     tree_of_lots['stage'][lot.stage_id.name][lot.rate_id.name] = []
        #
        # tree_of_lots['stage'][lot.stage_id.name][lot.rate_id.name].append({
        #     'id': lot.procurement_id,
        #     'unit_name': lot.unit_id.name
        # })

    # most_common_lots_by_stage_name = [i for i in Counter(lot['stage_name'] for lot in list_of_lots).most_common(20)]
    # list_of_lots = [x for x in list_of_lots if x['stage_name'] in most_common_lots_by_stage_name]

    print(sheet['B18'].value)
