import base64
from json import JSONDecodeError

import requests
import streamlit as st

api = 'http://127.0.0.1:5001/api/create_proposal'
st.set_page_config(layout="wide")
container = st.container


def send_request(segment_name=None, sub_segment_name=None, service_code=None, service_name=None,
                 subject=None, guaranteed_volume=None):
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json; text/plain'
    }
    try:
        # "http://127.0.0.1:5001/api/create_proposal"
        # "http://192.168.10.37:8517/api/create_proposal"
        response = requests.post(
            "http://127.0.0.1:5001/api/create_proposal",
            headers=headers,
            json={
                'segmet': segment_name,
                'sub_segment': sub_segment_name,
                'service_code': service_code,
                'service_name': service_name,
                'subject': subject,
                'guaranteed_volume': False if guaranteed_volume == 'False' else True
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


def send_request_for_compare_proposal(excel_in_base64, procurement_id):
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json; text/plain'
    }
    try:
        # "http://127.0.0.1:5001/api/create_proposal"
        # "http://192.168.10.37:8517/api/create_proposal"
        response = requests.post(
            "http://127.0.0.1:5001/api/compare_proposal_from_initiator",
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


def get_download_link():
    data = send_request(st.session_state['segment'],
                        st.session_state['sub_segment'],
                        st.session_state['service_code'],
                        st.session_state['service_name'],
                        st.session_state['subject'],
                        st.session_state['guaranteed_volume'])
    if data.get('message'):
        return data.get('message'), False
    return f'<a href="data:file/xlsm;base64,{data["proposal_file"]}" download="{data["name"]}">Download xlsm file</a>', True


for key in ['subject', 'segment', 'sub_segment', 'service_code', 'service_name', 'guaranteed_volume']:
    if key not in st.session_state:
        st.session_state[key] = ""

st.session_state['subject'] = 'Где деньги,Лебовски?'
st.session_state['segment'] = 'Корпоратив защита и защита информации'
st.session_state['sub_segment'] = '-'
st.session_state['service_code'] = '90303'
st.session_state['service_name'] = 'Услуги по охране объектов и (или) имущества (в том числе при его транспортировке)'
st.session_state['guaranteed_volume'] = False

st.session_state['subject'] = st.text_input('Предмет закупки', st.session_state['subject'])
st.session_state['segment'] = st.text_input('Сегмент закупки', st.session_state['segment'])
st.session_state['sub_segment'] = st.text_input('Подсегмент закупки', st.session_state['sub_segment'])
st.session_state['service_code'] = st.text_input('Код услуги', st.session_state['service_code'])
st.session_state['service_name'] = st.text_input('Наименование услуги', st.session_state['service_name'])
st.session_state['guaranteed_volume'] = st.text_input('Признак наличия гарантированного объема',
                                                      st.session_state['guaranteed_volume'])
btn = st.button("Отправить запрос")

if btn:
    link, has_error = get_download_link()
    if has_error is False:
        st.write(link)
    else:
        st.markdown(link, unsafe_allow_html=True)

file_uploader = st.file_uploader("Выберите файл", ["xlsm"])

if file_uploader:
    encode = base64.b64encode(file_uploader.getvalue()).decode('UTF-8')
    send_request_for_compare_proposal(encode, '0')
