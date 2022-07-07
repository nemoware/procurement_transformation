import numpy as np
import pandas as pd
import peewee
from tqdm import tqdm
from db import db_init
from db.entity.lot import Lot
from db.entity.simple_entity import *


def parse_reference_book() -> None:
    df = pd.read_excel(open('УПРОЩ. КП ВР (Анализ рынка. Работы-Услуги)_v4_5.xlsm', 'rb'), sheet_name='Справочник')
    list_of_trees = []
    for index, row in tqdm(df.iterrows(), desc="Generate lots", total=df.shape[0]):
        rate, segment, service, stage, sub_segment, unit, = get_or_create(row)
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
                    'stages': []
                }
                list_of_trees.append(tree_of_lots)

            if not tree_of_lots['stages']:
                for ind, id_from_list in enumerate(list(range(1, int(number_of_services) + 1))):
                    tree_of_lots['stages'].append({
                        'procurement_id': id_from_list,
                        'stage_name': stage[0].name,
                        'stage_id': stage[0].id,
                        'rates': {},
                        'count': number_of_services
                    })

            interval_of_rates = [i for i, element in enumerate(tree_of_lots['stages']) if
                                 element['rates'].get(rate[0].name, False)]

            if not interval_of_rates:
                interval_of_rates = list(range(number_of_services))
                interval_of_rates.sort(key=lambda x: len(tree_of_lots['stages'][x]['rates']))
                for ind in range(number_of_rates):
                    tree_of_lots['stages'][interval_of_rates[ind]]['rates'][rate[0].name] = {
                        'rate_id': rate[0].id,
                        'units': {},
                        'count': number_of_rates
                    }
            else:
                interval_of_rates.sort(key=lambda x: len(tree_of_lots['stages'][x]['rates']))

            ids = [i for i, element in enumerate(tree_of_lots['stages']) if
                   element['rates'].get(rate[0].name, False)]

            if not ids:
                print('rate is not exist')
                continue

            ids.sort(key=lambda x: len(tree_of_lots['stages'][x]['rates'][rate[0].name]['units']))

            j = 0
            for ind, id in enumerate(ids):
                is_exist = tree_of_lots['stages'][id]['rates'][rate[0].name]['units'].get(unit[0].name, False)
                if not is_exist:
                    tree_of_lots['stages'][id]['rates'][rate[0].name]['units'][unit[0].name] = {
                        'unit_id': unit[0].id,
                        'count': number_of_units
                    }
                    j += 1
                if j == number_of_units:
                    break

    for tree in tqdm(list_of_trees, desc="Save lots"):
        for stage in tree['stages']:
            for rate in stage['rates']:
                for unit in stage['rates'][rate]['units']:
                    try:
                        Lot.create(procurement_id=stage["procurement_id"],
                                   segment_id=tree["segment_id"],
                                   sub_segment_id=tree["sub_segment_id"],
                                   service_code=tree["service_code"],
                                   stage_id=stage["stage_id"],
                                   rate_id=stage['rates'][rate]['rate_id'],
                                   unit_id=stage['rates'][rate]['units'][unit]['unit_id'],
                                   is_from_excel=True)
                    except Exception as e:
                        print(f'{tree["segment_name"]} {tree["sub_segment_name"]} {tree["service_code"]} '
                              f'{stage["procurement_id"]} {stage["stage_name"]} {rate} {unit}')
                        print(e)
                    finally:
                        continue
    print('rate')


def get_or_create(row):
    segment = Segment.get_or_create(name=row['Сегмент'])
    sub_segment = Sub_segment.get_or_create(name=row['Подсегмент'])
    service = Service.get_or_create(code=row['Код услуги '], name=row['Наименование услуги'])
    stage = Stage.get_or_create(name=row['Наименование этапов/подэтапов услуг/работ'])
    rate = Rate.get_or_create(name=row['Наименование расценок'])
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
        print('Can`t create tables')
