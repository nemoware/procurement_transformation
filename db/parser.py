import numpy as np
import pandas as pd
from tqdm import tqdm

from db.entity.lot import Lot
from db.entity.simple_entity import *


def parse_reference_book() -> None:
    df = pd.read_excel(open('УПРОЩ. КП ВР (Анализ рынка. Работы-Услуги)_v4_5.xlsm', 'rb'), sheet_name='Справочник')

    for index, row in tqdm(df.iterrows(), desc="Load and save simple tables from excel", total=df.shape[0]):
        get_or_create(row)

    for index, row in tqdm(df.iterrows(), desc="Generate lots", total=df.shape[0]):
        rate, segment, service, stage, sub_segment, unit, amount = get_or_create(row)
        if amount is not None and not np.isnan(amount):
            for i in range(int(amount) + 1):
                if i == 0:
                    Lot.create(
                        segment_id=segment[0].id,
                        sub_segment_id=sub_segment[0].id,
                        service_code=service[0].code,
                        stage_id=stage[0].id,
                        rate_id=rate[0].id,
                        unit_id=unit[0].id,
                        is_null=True
                    )
                    continue
                Lot.create(
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
    amount = row['Количество закупок по ЕИ']
    return rate, segment, service, stage, sub_segment, unit, amount
