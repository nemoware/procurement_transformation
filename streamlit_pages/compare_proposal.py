import base64
from json import JSONDecodeError

import requests
import streamlit as st

from api.common import env_var

api = env_var('URL_API', 'http://127.0.0.1:5001')


def send_request_for_compare_proposal(excel_in_base64, procurement_id):
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json; text/plain'
    }
    try:
        # "http://127.0.0.1:5001/api/create_proposal"
        # "http://192.168.10.37:8517/api/create_proposal"
        response = requests.post(
            f"{api}/api/compare_proposal_from_initiator",
            headers=headers,
            json={
                'proposal_file': excel_in_base64,
                'procurement_id': procurement_id,
            }
        )
        response_json = response.json()
        return response_json
    except JSONDecodeError:
        print('Decoding JSON has failed')
        return False
    except requests.exceptions.RequestException:
        print("Ошибка при запросе")
        return False


def run():
    file_uploader = st.file_uploader("Выберите файл", ["xlsm"])

    if file_uploader:
        encode = base64.b64encode(file_uploader.getvalue()).decode('UTF-8')
        send_request_for_compare_proposal(encode, '0')
