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
                'procurement_id': str(procurement_id),
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


def send_request(procurement_id: str):
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json; text/plain'
    }
    try:
        response = requests.post(
            f"{api}/api/get_by_id",
            headers=headers,
            json={
                'procurement_id': procurement_id
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


def get_download_link():
    data = send_request(str(st.session_state['procurement_id2']))
    if data.get('message'):
        return data.get('message'), False
    return f'<a href="data:file/xlsm;base64,{data["proposal_file"]}" download="{data["name"]}">Download xlsm file</a>', True


def run():
    for key in ['procurement_id', 'procurement_id2']:
        if key not in st.session_state:
            st.session_state[key] = 85

    st.session_state['procurement_id2'] = st.text_input('ИД закупки', st.session_state['procurement_id2'], key='ID2')
    btn2 = st.button("Получить закупку")

    file_uploader = st.file_uploader("Выберите файл", ["xlsm"])
    st.session_state['procurement_id'] = st.text_input('ИД закупки', st.session_state['procurement_id'])
    btn = st.button("Отправить запрос")

    if file_uploader and btn:
        encode = base64.b64encode(file_uploader.getvalue()).decode('UTF-8')
        response = send_request_for_compare_proposal(encode, st.session_state['procurement_id'])
        st.write(response)

    if btn2:
        link, has_error = get_download_link()
        if has_error is False:
            st.write(link)
        else:
            st.markdown(link, unsafe_allow_html=True)
