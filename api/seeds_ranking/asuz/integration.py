import urllib.parse

import requests

from api.common import env_var


def get_auth_token():
    auth_url = urllib.parse.urljoin(env_var('ASUZ_API_URL'), '/api/Auth')
    asuz_api_login = env_var('ASUZ_API_LOGIN', '')
    asuz_api_password = env_var('ASUZ_API_PASSWORD', '')
    response = requests.post(url=auth_url, data={'login': asuz_api_login, 'password': asuz_api_password})
    if response.status_code != 200:
        raise Exception(f'Cannot get access token from {auth_url}')
    response_json = response.json()
    return response_json['access_token']


def get_procurements():
    auth_token = get_auth_token()
    headers = {"Authorization": "Bearer " + auth_token}
    request_url = urllib.parse.urljoin(env_var('ASUZ_API_URL'), '/api/SapDataBook/NamePurchaseItems')
    resp = requests.get(url=request_url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Cannot load lots from ASUZ')
    data = resp.json()
    return data
