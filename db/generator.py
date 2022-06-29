from openpyxl import load_workbook


def generate_():
    workbook = load_workbook(filename="Пустой шаблон.xlsm")
    sheet = workbook["Форма КП (для анализа рынка) ВР"]
    sheet_reference_book = workbook["Справочник"]

    print(sheet['B18'].value)
