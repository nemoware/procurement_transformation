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

    for num in [6, 8, 9, 10, 11]:
        if ws[f'C{num}'].value is None:
            raise ValueError(f'Ошибка в шапке файла, а именно в ячейке C{num}')
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
    for index, row in enumerate(ws.iter_rows(min_row=18, max_col=8, values_only=True), start=18):
        if is_stopped:
            break
        for ind, cell in enumerate(row, start=1):
            if ind == 1 and (row[1] == ('Командировочные расходы \n'
                                        '(При необходимости. Включаются в стоимость КП, '
                                        'если в ТЗ не заявлено требование об оказании услуг/выполнения работ в '
                                        'удаленном формате и/или для оказании услуг/выполнения работ требуется '
                                        'оформление командировки для указанного выше состава исполнителей)') or
                             row[1] == 'Всего без НДС'):
                is_stopped = True
                break

            if ind == 1:
                if cell != f'=ROW(A{index})-17':
                    raise ValueError(f'Не правильно указана формула в 1 столбец, в строке {index}, '
                                     f'должно быть значение =ROW(A{index})-17, а было найдено {cell}')
            if ind == 2:
                if cell == 'Итого:':
                    prev_stage_name = None
                    break
                if prev_stage_name is None:
                    if type(cell) is not str and len(cell) == 0:
                        raise ValueError(f'Не был указан этап в строке {index}')
                    prev_stage_name = cell

            if ind == 3 and (type(cell) is not str or cell is None or len(cell) == 0):
                raise ValueError(f'Не правильно указан этап в строке {index}')

            if ind == 5 and (type(cell) is not str or cell is None or len(cell) == 0):
                raise ValueError(f'Не правильно указана расценка в строке {index}')

            if (ind == 6 or ind == 7) and ((type(cell) is not int and type(cell) is not float) or cell < 0):
                raise ValueError(
                    f'Не правильно указано значение в {"Кол-во ЕИ" if ind == 6 else "Стоимость ЕИ в валюте Участника"},'
                    f'в строке {index}')

            if ind == 8 and cell != f'=F{index}*G{index}':
                raise ValueError(
                    f'Ошибка в формуле в столбец \"ИТОГО в валюте Участника\", '
                    f'в строке {index}')
    return True
