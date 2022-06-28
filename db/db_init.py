import pandas as pd
import peewee

from db.config import db_handle
from db.entity.lot import Lot
from db.entity.rate import Rate
from db.entity.segment import Segment
from db.entity.service import Service
from db.entity.stage import Stage
from db.entity.sub_segment import Sub_segment
from db.entity.unit import Unit


def create_table() -> bool:
    try:
        db_handle.connect()
        Unit.create_table(safe=True)
        Sub_segment.create_table(safe=True)
        Stage.create_table(safe=True)
        Service.create_table(safe=True)
        Segment.create_table(safe=True)
        Rate.create_table(safe=True)
        Lot.create_table(safe=True)
        parse_reference_book()
        return True
    except peewee.InternalError as px:
        print(str(px))
        return False


def parse_reference_book():
    df = pd.read_excel(open('УПРОЩ. КП ВР (Анализ рынка. Работы-Услуги)_v4_5.xlsm', 'rb'), sheet_name='Справочник')
    print('first circle')
    for index, row in df.iterrows():
        get_or_create(row)
    print('second circle')
    for index, row in df.iterrows():
        rate, segment, service, stage, sub_segment, unit = get_or_create(row)
        lot, created = Lot.get_or_create(
            segment_id=segment[0].id,
            sub_segment_id=sub_segment[0].id,
            service_code=service[0].code,
            stage_id=stage[0].id,
            rate_id=rate[0].id,
            unit_id=unit[0].id,
        )


def get_or_create(row):
    segment = Segment.get_or_create(name=row['Сегмент'])
    sub_segment = Sub_segment.get_or_create(name=row['Подсегмент'])
    service = Service.get_or_create(code=row['Код услуги '], name=row['Наименование услуги'])
    stage = Stage.get_or_create(name=row['Наименование этапов/подэтапов услуг/работ'])
    rate = Rate.get_or_create(name=row['Наименование расценок'])
    unit = Unit.get_or_create(name=row['Наименование ЕИ'])
    return rate, segment, service, stage, sub_segment, unit
