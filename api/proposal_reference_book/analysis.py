import base64
from io import BytesIO

from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet

from db.entity.lot import Lot
from db.entity.simple_entity import Segment, Sub_segment, Service, Unit, Rate, Stage


def compare_proposal(proposal_file, procurement_id):
    wb = load_workbook(filename=BytesIO(base64.b64decode(proposal_file)))
    try:
        excel_validation(wb)
    except ValueError as e:
        raise ValueError(str(e))

    current_lots = (Lot.select(Lot, Segment, Sub_segment, Service, Stage, Rate, Unit)
                    .join(Segment).switch(Lot)
                    .join(Sub_segment).switch(Lot)
                    .join(Service).switch(Lot)
                    .join(Stage).switch(Lot)
                    .join(Rate).switch(Lot)
                    .join(Unit)
                    .where(Lot.procurement_id == procurement_id))
    list_of_lots_from_db = []

    for lot in current_lots:
        list_of_lots_from_db.append({
            'segment_name': lot.segment_id.name,
            'sub_segment_name': lot.sub_segment_id.name,
            'service_code': lot.service_code.code,
            'service_name': lot.service_code.name,
            'stage_name': lot.stage_id.name,
            'rate_name': lot.rate_id.name,
            'unit_name': lot.unit_id.name,
            'stage_id': lot.stage_id.id,
            'rate_id': lot.rate_id.id,
            'unit_id': lot.unit_id.id,
            'id': lot.procurement_id,
            'is_null': lot.is_null
        })
    del lot

    return {}


def excel_validation(wb: Workbook):
    ws: Worksheet = wb['Форма КП (для анализа рынка) ВР']
    words = [
        '№ п\п',
        'Наименование этапа / услуги (работы)',
        'Наименование расценки',
        'Альтернативное наименование расценки',
        'Единица измерения\n(ЕИ)',
        'Кол-во ЕИ',
        'Стоимость ЕИ\nв валюте Участника',
        'ИТОГО\nв валюте Участника',
    ]
    for ind, cell in enumerate(ws[15]):
        if cell.value != words[ind]:
            raise ValueError(f'Ошибка в наименовании столбца, должно быть {words[0]}, что было найдено {cell.value}')
    for ind, cell in enumerate(ws[17], start=1):
        if ind != cell.value:
            raise ValueError(f'В строке под номером 17, не правильно указаны числа')

    is_stopped = False
    prev_stage_name = None
    shift_index = 0
    for index, row in enumerate(ws.iter_rows(min_row=18, max_col=8, values_only=True), start=18):
        for ind, cell in enumerate(row, start=1):
            if ind == 1:
                number_from_cell = 0
                try:
                    number_from_cell = int(cell)
                except Exception as e:
                    raise ValueError(f'В 1-ом столбец, в строке {index}, указано что-то не похожее на число'
                                     f'--> {cell} <--')
                if (index - 17) != number_from_cell:
                    raise ValueError(f'Не правильно пронумерован 1 столбец в строке {index}, '
                                     f'должно быть значение {index - 17}, а было найдено {number_from_cell}')
            if ind == 2:
                if cell == 'Итого:':
                    break
                if prev_stage_name is None:
                    if type(cell) is not str and len(cell) == 0:
                        raise ValueError(f'Не был указан этап в строке {index}')
                    prev_stage_name = cell
            if cell == 'Итого:':
                prev_stage_name = None
                shift_index += 1
            if ind == 3 and type(cell) is not str and len(cell) == 0:
                raise ValueError(f'Не правильно указан этап в строке {index}')
            if ind == 5 and type(cell) is not str and len(cell) == 0:
                raise ValueError(f'Не правильно указана расценка в строке {index}')
            if (ind == 6 or ind == 7) and (type(cell) is not int and type(cell) is not float) and cell <= 0:
                raise ValueError(
                    f'Не правильно указано значение в {"Кол-во ЕИ" if ind == 6 else "Стоимость ЕИ в валюте Участника"},'
                    f'в строке {index}')
            if ind == 8 and cell != f'=F{index + shift_index}*G{index + shift_index}':
                raise ValueError(
                    f'Ошибка в формуле в столбец \"ИТОГО в валюте Участника\", '
                    f'в строке {index + shift_index}')
            print(cell)
        print(index)
    return True
