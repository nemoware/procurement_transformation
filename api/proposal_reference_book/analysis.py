import base64
from io import BytesIO

from openpyxl import load_workbook


def compare_proposal(proposal_file, procurement_id):
    wb = load_workbook(filename=BytesIO(base64.b64decode(proposal_file)))
    ws = wb['Справочник']
    return {}
