import logging

import numpy as np
import pandas as pd
import peewee
from tqdm import tqdm
from db import db_init
from db.entity.lot import Lot
from db.entity.simple_entity import *

logger = logging.getLogger(__name__)


def parse_reference_book() -> None:
    df = pd.read_excel(open('УПРОЩ. КП ВР (Анализ рынка. Работы-Услуги)_v4_5.xlsm', 'rb'), sheet_name='Справочник')
    list_of_trees = []
    rate = None
    segment, service, stage, sub_segment, unit = None, None, None, None, None
    unique_id = 0
    for index, row in tqdm(df.iterrows(), desc="Generate simple tables", total=df.shape[0]):
        rate, segment, service, stage, sub_segment, unit = get_or_create(row, rate, segment, service, stage,
                                                                         sub_segment, unit)

    for index, row in tqdm(df.iterrows(), desc="Generate lots", total=df.shape[0]):
        rate, segment, service, stage, sub_segment, unit = get_or_create(row, rate, segment, service, stage,
                                                                         sub_segment, unit)
        number_of_services, number_of_stages, number_of_rates, number_of_units = get_number_of(row)
        if number_of_units is not None and not np.isnan(number_of_units):
            if number_of_units == 0:
                Lot.get_or_create(
                    procurement_id=0,
                    segment_id=segment[0].id,
                    sub_segment_id=sub_segment[0].id,
                    service_code=service[0].code,
                    stage_id=stage[0].id,
                    rate_id=rate[0].id,
                    unit_id=unit[0].id,
                    is_null=True,
                    is_from_excel=True
                )
                continue
            tree_of_lots = next((
                item for item in list_of_trees if item["segment_name"] == segment[0].name and
                                                  item["sub_segment_name"] == sub_segment[0].name and
                                                  item["service_code"] == service[0].code
            ), False)

            if not tree_of_lots:
                tree_of_lots = {
                    'segment_name': segment[0].name,
                    'segment_id': segment[0].id,
                    'sub_segment_name': sub_segment[0].name,
                    'sub_segment_id': sub_segment[0].id,
                    'service_code': service[0].code,
                    'procurements': []
                }
                list_of_trees.append(tree_of_lots)

            if not tree_of_lots['procurements']:
                for ind, id_from_list in enumerate(list(range(1, int(number_of_services) + 1))):
                    unique_id += 1
                    tree_of_lots['procurements'].append({
                        'procurement_id': 'арх' + str(unique_id),
                        'stages': {},
                        'count': number_of_services
                    })

            interval_of_procurements = [i for i, element in enumerate(tree_of_lots['procurements']) if
                                        element['stages'].get(stage[0].name, False)]

            if not interval_of_procurements:
                interval_of_procurements = list(range(number_of_services))
                interval_of_procurements.sort(key=lambda x: len(tree_of_lots['procurements'][x]['stages']))
                for ind in range(number_of_stages):
                    tree_of_lots['procurements'][interval_of_procurements[ind]]['stages'][stage[0].name] = {
                        'stage_id': stage[0].id,
                        'rates': {},
                    }

            interval_of_rates = [i for i, element in enumerate(tree_of_lots['procurements']) if
                                 element['stages'].get(stage[0].name, {'rates': {}})['rates'].get(rate[0].name, False)]

            if not interval_of_rates:
                interval_of_rates = [i for i, element in enumerate(tree_of_lots['procurements']) if
                                     element['stages'].get(stage[0].name, False)]
                interval_of_rates.sort(
                    key=lambda x: len(
                        tree_of_lots['procurements'][x]['stages'].get(stage[0].name, {'rates': []})['rates'])
                )
                for ind in range(number_of_rates):
                    if not tree_of_lots['procurements'][interval_of_rates[ind]]['stages'].get(stage[0].name, False):
                        tree_of_lots['procurements'][interval_of_rates[ind]]['stages'][stage[0].name] = {
                            'stage_id': stage[0].id,
                            'rates': {},
                        }
                    tree_of_lots['procurements'][interval_of_rates[ind]]['stages'][stage[0].name]['rates'][
                        rate[0].name] = {
                        'rate_id': rate[0].id,
                        'units': {}
                    }

            interval_of_units = [i for i, element in enumerate(tree_of_lots['procurements']) if
                                 (
                                     element['stages']
                                     .get(stage[0].name, {'rates': {}})['rates']
                                     .get(rate[0].name, False)
                                 )]

            interval_of_units.sort(
                key=lambda x: len(
                    tree_of_lots['procurements'][x]['stages']
                    .get(stage[0].name, {'rates': {}})['rates']
                    .get(rate[0].name, {'units': {}})['units']
                )
            )
            j = 0
            for ind in interval_of_units:
                is_exist = tree_of_lots['procurements'][ind]['stages'][stage[0].name]['rates'][rate[0].name][
                    'units'].get(unit[0].name, False)
                if not is_exist:
                    tree_of_lots['procurements'][ind]['stages'][stage[0].name]['rates'][rate[0].name][
                        'units'][unit[0].name] = {
                        'unit_id': unit[0].id
                    }
                    j += 1
                if j == number_of_units:
                    break

    for tree in tqdm(list_of_trees, desc="Save lots"):
        if tree["service_code"] == '90303':
            logger.debug(123)
        for procurement in tree['procurements']:
            for stage in procurement['stages']:
                for rate_key in procurement['stages'][stage]['rates']:
                    for unit_key in procurement['stages'][stage]['rates'][rate_key]['units']:
                        try:
                            Lot.create(procurement_id=procurement["procurement_id"],
                                       segment_id=tree["segment_id"],
                                       sub_segment_id=tree["sub_segment_id"],
                                       service_code=tree["service_code"],
                                       stage_id=procurement['stages'][stage]['stage_id'],
                                       rate_id=procurement['stages'][stage]['rates'][rate_key]['rate_id'],
                                       unit_id=procurement['stages'][stage]['rates'][rate_key]['units'][unit_key][
                                           'unit_id'],
                                       is_from_excel=True)
                        except Exception as e:
                            logger.exception(
                                f'{tree["segment_name"]} {tree["sub_segment_name"]} {tree["service_code"]} '
                                f'{stage["procurement_id"]} {stage["stage_name"]} {rate_key} {unit_key}')
                            logger.exception(e)


def get_or_create(row, rate, segment, service, stage, sub_segment, unit):
    if rate is None or rate[0].name != row['Наименование расценок']:
        rate = Rate.get_or_create(name=row['Наименование расценок'])

    if segment is None or segment[0].name != row['Сегмент']:
        segment = Segment.get_or_create(name=row['Сегмент'])

    if service is None or service[0].name != row['Наименование услуги'] and service[0].code != row['Код услуги ']:
        service = Service.get_or_create(code=row['Код услуги '], name=row['Наименование услуги'])

    if stage is None or stage[0].name != row['Наименование этапов/подэтапов услуг/работ']:
        stage = Stage.get_or_create(name=row['Наименование этапов/подэтапов услуг/работ'])

    if sub_segment is None or sub_segment[0].name != row['Подсегмент']:
        sub_segment = Sub_segment.get_or_create(name=row['Подсегмент'])

    if unit is None or unit[0].name != row['Наименование ЕИ']:
        unit = Unit.get_or_create(name=row['Наименование ЕИ'])

    return rate, segment, service, stage, sub_segment, unit


def get_number_of(row):
    number_of_services = row['Количество']
    number_of_stages = row['Количество закупок по этапам']
    number_of_rates = row['Количестов закупок по наименованиям расценок']
    number_of_units = row['Количество закупок по ЕИ']
    return int(number_of_services), int(number_of_stages), int(number_of_rates), int(number_of_units)


if __name__ == "__main__":
    if db_init.create_table():
        parse_reference_book()
    else:
        logger.error('Can`t create tables')
