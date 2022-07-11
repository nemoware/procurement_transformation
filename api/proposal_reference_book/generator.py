import base64
from copy import copy
import itertools
import os
import shutil

from openpyxl import load_workbook, Workbook
from peewee import fn, SQL

from db.entity.lot import Lot
from db.entity.simple_entity import Segment, Sub_segment, Service, Unit


def generate_prefilled_proposal(segment_name=None, sub_segment_name=None, service_code=None, service_name=None,
                                subject=None, guaranteed_volume=None):
    # segment_name = 'Корпоратив защита и защита информации'
    # sub_segment_name = '-'
    # service_code = '90303'
    # service_name = 'Услуги по охране объектов и (или) имущества (в том числе при его транспортировке)'

    list_of_stage_ids = []
    list_of_rate_ids = []

    current_stage_ids = (Lot.select(Lot.stage_id, fn.COUNT(Lot.stage_id).alias('num_stage_id'))
                         .join(Segment).switch(Lot)
                         .join(Sub_segment).switch(Lot)
                         .join(Service).switch(Lot)
                         .where(Segment.name == segment_name, Sub_segment.name == sub_segment_name,
                                Service.code == service_code)
                         .group_by(Lot.stage_id)
                         .order_by(SQL('num_stage_id').desc()))

    for lot in current_stage_ids:
        list_of_stage_ids.append({
            'stage_id': lot.stage_id.id,
            'num_stage_id': lot.num_stage_id
        })

    list_of_stage_ids = list_of_stage_ids[:5]

    current_rate_ids = (Lot.select(Lot.rate_id, fn.COUNT(Lot.stage_id).alias('num_rate_id'))
                        .join(Segment).switch(Lot)
                        .join(Sub_segment).switch(Lot)
                        .join(Service).switch(Lot)
                        .where((Segment.name == segment_name) &
                               (Sub_segment.name == sub_segment_name) &
                               (Service.code == service_code) &
                               (Lot.stage_id << list(map(lambda x: x['stage_id'], list_of_stage_ids))))
                        .group_by(Lot.rate_id)
                        .order_by(SQL('num_rate_id').desc()))

    for lot in current_rate_ids:
        list_of_rate_ids.append({
            'rate_id': lot.rate_id.id,
            'num_rate_id': lot.num_rate_id
        })
    list_of_rate_ids = list_of_rate_ids[:10]

    current_lots = (Lot.select(Lot)
                    .join(Segment).switch(Lot)
                    .join(Sub_segment).switch(Lot)
                    .join(Service).switch(Lot)
                    .join(Unit)
                    .where((Segment.name == segment_name) &
                           (Sub_segment.name == sub_segment_name) &
                           (Service.code == service_code) &
                           (Lot.stage_id << list(map(lambda x: x['stage_id'], list_of_stage_ids))) &
                           (Lot.rate_id << list(map(lambda x: x['rate_id'], list_of_rate_ids))))
                    )

    list_of_lots = []
    if len(list_of_stage_ids) == 0 or len(list_of_rate_ids) == 0:
        raise ValueError('По данному запросу не были найдены этапы или расценки')

    del list_of_stage_ids, list_of_rate_ids, current_rate_ids, current_stage_ids

    for lot in current_lots:
        list_of_lots.append({
            'id': lot.procurement_id,
            'segment_name': lot.segment_id.name,
            'sub_segment_name': lot.sub_segment_id.name,
            'service_code': lot.service_code.code,
            'stage_name': lot.stage_id.name,
            'stage_id': lot.stage_id.id,
            'rate_name': lot.rate_id.name,
            'rate_id': lot.rate_id.id,
            'unit_name': lot.unit_id.name,
            'unit_id': lot.unit_id.id,
        })
    del current_lots

    current_lots = (Lot.select(Lot)
                    .join(Segment).switch(Lot)
                    .join(Sub_segment).switch(Lot)
                    .join(Service).switch(Lot)
                    .join(Unit)
                    .where((Segment.name == segment_name) &
                           (Sub_segment.name == sub_segment_name) &
                           (Service.code == service_code) &
                           (Lot.procurement_id != '0')))

    list_of_all_lots = []
    for lot in current_lots:
        list_of_all_lots.append({
            'segment_name': lot.segment_id.name,
            'sub_segment_name': lot.sub_segment_id.name,
            'service_code': lot.service_code.code,
            'service_name': lot.service_code.name,
            'number_of_service': 0,
            'stage_name': lot.stage_id.name,
            'number_of_stages': 0,
            'percent_of_stages': 0,
            'rate_name': lot.rate_id.name,
            'number_of_rates': 0,
            'percent_of_rates': 0,
            'unit_name': lot.unit_id.name,
            'number_of_units': 0,
            'percent_of_units': 0,
            'stage_id': lot.stage_id.id,
            'rate_id': lot.rate_id.id,
            'unit_id': lot.unit_id.id,
            'id': lot.procurement_id,
        })
    del current_lots

    number_of_all_stages = {}
    list_if_ids = list(sorted(set(map(lambda x: x['id'], list_of_all_lots)), key=lambda x: int(x[3:])))
    number_of_ids = len(list_if_ids)
    list_of_stage_name = []

    for id in list_if_ids:
        lots = [single_lot for single_lot in list_of_all_lots if single_lot['id'] == id]
        for lot in lots:
            stage_name = lot['stage_name']
            rate_name = lot['rate_name']
            unit_name = lot['unit_name']
            number_of_all_stages.setdefault(stage_name, {
                'count': 0
            })
            if stage_name not in list_of_stage_name:
                number_of_all_stages[stage_name]['count'] += 1
                list_of_stage_name.append(stage_name)

            number_of_all_stages[stage_name].setdefault(rate_name, {
                'count': 0
            })['count'] += 1
            number_of_all_stages[stage_name][rate_name].setdefault(unit_name, {
                'count': 0
            })['count'] += 1
        list_of_stage_name = []

    del list_if_ids, lots, stage_name, rate_name, unit_name, id

    for lot in list_of_all_lots:
        lot['number_of_service'] = number_of_ids
        lot['number_of_stages'] = number_of_all_stages[lot['stage_name']]['count']
        lot['number_of_rates'] = number_of_all_stages[lot['stage_name']][lot['rate_name']]['count']
        lot['number_of_units'] = number_of_all_stages[lot['stage_name']][lot['rate_name']][lot['unit_name']]['count']

    list_of_lots = list(filter(lambda x: x['id'] != '0', list_of_lots))
    list_of_lots.sort(
        key=lambda x: (
            number_of_all_stages[x['stage_name']]['count'],
            number_of_all_stages[x['stage_name']][x['rate_name']]['count'],
            number_of_all_stages[x['stage_name']][x['rate_name']][x['unit_name']]['count']
        ), reverse=True
    )
    list_without_duplicates_of_lots = []
    for element in list_of_lots:
        del element['id']
    del element

    seen = set()
    for d in list_of_lots:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            list_without_duplicates_of_lots.append(d)
    for lot in list_without_duplicates_of_lots:
        del lot['rate_id'], lot['stage_id'], lot['unit_id']
    del seen, d, t, list_of_lots, lot

    list_of_all_lots.sort(
        key=lambda x: (
            number_of_all_stages[x['stage_name']]['count'],
            number_of_all_stages[x['stage_name']][x['rate_name']]['count'],
            number_of_all_stages[x['stage_name']][x['rate_name']][x['unit_name']]['count']
        ), reverse=True
    )

    for element in list_of_all_lots:
        del element['id']
    del element, number_of_ids

    list_without_duplicates_of_all_lots = []
    seen = set()
    for d in list_of_all_lots:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            list_without_duplicates_of_all_lots.append(d)
    del seen, d, t, list_of_all_lots

    shutil.copy("Пустой шаблон.xlsm", f"{service_code} {segment_name} {sub_segment_name}.xlsm")

    workbook = load_workbook(filename=f"{service_code} {segment_name} {sub_segment_name}.xlsm", read_only=False,
                             keep_vba=True)

    ws = workbook["Форма КП (для анализа рынка) ВР"]
    index_of_number = 1
    ws['C6'] = subject
    ws['C8'] = segment_name
    ws['C9'] = sub_segment_name
    ws['C10'] = service_code
    ws['C11'] = service_name

    list_without_duplicates_of_lots.sort(key=lambda x: x['stage_name'])
    list_without_duplicates_of_lots.sort(key=lambda x: (
        number_of_all_stages[x['stage_name']]['count']
    ), reverse=True)
    prev_stage_name = None
    start_index = 0
    end_index = 0
    shift_index = 0
    for index, lot in enumerate(list_without_duplicates_of_lots, start=18):
        if prev_stage_name is None:
            prev_stage_name = lot['stage_name']
            start_index = index
        if prev_stage_name == lot['stage_name']:
            end_index = index + shift_index
        else:
            ws.merge_cells(start_row=start_index, start_column=2, end_row=end_index, end_column=2)
            ws.append([
                index_of_number, 'Итого:', '', '', '',
                f'=SUM(F{start_index}:F{end_index})',
                f'=SUM(G{start_index}:G{end_index})',
                f'=SUM(H{start_index}:H{end_index})',
            ])
            ws.merge_cells(start_row=end_index + 1, start_column=2, end_row=end_index + 1, end_column=4)
            shift_index += 1
            start_index = index + shift_index
            end_index = index + shift_index
            prev_stage_name = lot['stage_name']
            index_of_number += 1

        lot = list(lot.values())
        del lot[0:3]
        lot.insert(0, index_of_number)
        lot.insert(3, 'Заполняется при необходимости. См. пояснения п.3.')
        lot.extend([0, 0, 0])
        ws.append(lot)
        index_of_number += 1

    ws.merge_cells(start_row=start_index, start_column=2, end_row=end_index, end_column=2)
    ws.append([
        index_of_number, 'Итого:', '', '', '',
        f'=SUM(F{start_index}:F{end_index})',
        f'=SUM(G{start_index}:G{end_index})',
        f'=SUM(H{start_index}:H{end_index})',
    ])
    ws.merge_cells(start_row=end_index + 1, start_column=2, end_row=end_index + 1, end_column=4)

    ws2 = workbook['footer']

    for row_index in range(1, 16):
        for column_index in range(1, 9):
            cell = ws2.cell(row=row_index, column=column_index)
            print(f'row {row_index} column {column_index}')
            new_cell = ws.cell(row=row_index + 1 + end_index, column=column_index)
            new_cell.value = copy(cell.value)
            copy_style(cell, new_cell)
    workbook.remove_sheet(ws2)

    ws[f'F{end_index + 4}'].value = f'=F{end_index + 2}'
    ws[f'H{end_index + 4}'].value = f'=H{end_index + 2}+H{end_index + 3}'
    for ind in range(2, 5):
        ws.merge_cells(start_row=end_index + ind,
                       start_column=2,
                       end_row=end_index + ind,
                       end_column=3)

    ws.merge_cells(start_row=end_index + 6,
                   start_column=1,
                   end_row=end_index + 7,
                   end_column=8)
    for ind in [10, 13, 16]:
        ws.merge_cells(start_row=end_index + ind,
                       start_column=3,
                       end_row=end_index + ind,
                       end_column=5)

    ws = workbook["Справочник"]
    for index, lot in enumerate(list_without_duplicates_of_all_lots, start=1):
        ws.append(list(lot.values()))

    workbook.save(filename=f"{service_code} {segment_name} {sub_segment_name}.xlsm")
    data = open(f"{service_code} {segment_name} {sub_segment_name}.xlsm", 'rb').read()
    this_is_base64 = base64.b64encode(data).decode('UTF-8')

    return {
        'proposal_file': this_is_base64,
        'name': f"{service_code} {segment_name} {sub_segment_name}.xlsm",
        'size': os.path.getsize(f"{service_code} {segment_name} {sub_segment_name}.xlsm")
    }


def is_duplicate(lot, lot2) -> bool:
    return (lot2['is_null'] is not True and
            lot['is_null'] is not True and
            lot2['segment_name'] == lot['segment_name'] and
            lot2['sub_segment_name'] == lot['sub_segment_name'] and
            lot2['service_code'] == lot['service_code'])


def copy_style(cell, new_cell):
    if cell.has_style:
        new_cell.font = copy(cell.font)
        new_cell.border = copy(cell.border)
        new_cell.fill = copy(cell.fill)
        new_cell.number_format = copy(cell.number_format)
        new_cell.protection = copy(cell.protection)
        new_cell.alignment = copy(cell.alignment)
