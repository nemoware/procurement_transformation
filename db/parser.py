import numpy as np
import pandas as pd
import peewee
from tqdm import tqdm
from db import db_init
from db.entity.lot import Lot
from db.entity.simple_entity import *


def parse_reference_book() -> None:
    df = pd.read_excel(open('УПРОЩ. КП ВР (Анализ рынка. Работы-Услуги)_v4_5.xlsm', 'rb'), sheet_name='Справочник')
    start_index = 1
    start_segment = ''
    start_sub_segment = ''
    start_service = ''
    start_stage = ''
    for index, row in tqdm(df.iterrows(), desc="Generate lots", total=df.shape[0]):
        rate, segment, service, stage, sub_segment, unit, amount, procurement_amount = get_or_create(row)
        if amount is not None and not np.isnan(amount):

            if (start_segment != segment[0].id and
                    start_sub_segment != sub_segment[0].id and
                    start_service != service[0].id and
                    start_stage != stage[0].id):
                start_index = 1
            if service[0].code == '11146':
                print('Starting')
            if start_index == 1:
                interval_of_ids = list(range(1, int(amount) + 1))
                start_segment = segment[0].id
                start_sub_segment = sub_segment[0].id
                start_service = service[0].code
                start_stage = stage[0].id
            else:
                interval_of_ids = list(range(start_index + 1, int(procurement_amount) + 1))
                length = int(amount)

                if len(interval_of_ids) != length:
                    interval_of_ids.extend(list(range(1, (length - len(interval_of_ids)) + 1)))

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
            # is_not_id_exist = True
            # while is_not_id_exist:
            # is_not_id_exist = False
            for i, index_from_list in enumerate(interval_of_ids):
                # lot = Lot.get_or_none(procurement_id=index_from_list,
                #                       segment_id=segment[0].id,
                #                       sub_segment_id=sub_segment[0].id,
                #                       service_code=service[0].code,
                #                       stage_id=stage[0].id,
                #                       rate_id=rate[0].id,
                #                       unit_id=unit[0].id,
                #                       is_from_excel=True)

                # if lot is not None:
                #     interval_of_ids = interval_of_ids[i:]
                #     interval_of_ids.append(interval_of_ids[0])
                #     interval_of_ids = interval_of_ids[1:]
                #     is_not_id_exist = True
                #     start_index = index_from_list
                #     break

                # try:
                Lot.create(procurement_id=index_from_list,
                           segment_id=segment[0].id,
                           sub_segment_id=sub_segment[0].id,
                           service_code=service[0].code,
                           stage_id=stage[0].id,
                           rate_id=rate[0].id,
                           unit_id=unit[0].id,
                           is_from_excel=True)
                # except peewee.IntegrityError as px:
                #     print('service[0].code ' + str(service[0].code))
                #     print('rate[0].code ' + str(rate[0].name))
                #     print('unit[0].code ' + str(unit[0].name))
                #     print('amount ' + str(amount))
                #     print(px)
                start_index = index_from_list
                # is_not_id_exist = False


def get_or_create(row):
    segment = Segment.get_or_create(name=row['Сегмент'])
    sub_segment = Sub_segment.get_or_create(name=row['Подсегмент'])
    service = Service.get_or_create(code=row['Код услуги '], name=row['Наименование услуги'])
    stage = Stage.get_or_create(name=row['Наименование этапов/подэтапов услуг/работ'])
    rate = Rate.get_or_create(name=row['Наименование расценок'])
    unit = Unit.get_or_create(name=row['Наименование ЕИ'])
    amount = row['Количество закупок по ЕИ']
    procurement_amount = row['Количество закупок по этапам']
    return rate, segment, service, stage, sub_segment, unit, amount, procurement_amount


if __name__ == "__main__":
    if db_init.create_table():
        parse_reference_book()
    else:
        print('Can`t create tables')
