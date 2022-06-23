import urllib.parse

import requests

from api.common import env_var


def get_auth_token():
    auth_url = urllib.parse.urljoin(env_var('ASUZ_API_URL'), '/api/Auth')
    response = requests.post(url=auth_url, )
    if response.status_code != 200:
        raise Exception(f'Cannot get access token from {auth_url}')
    response_json = response.json()
    return response_json['access_token']


def get_procurements():
    auth_token = get_auth_token()
    headers = {"Authorization": "Bearer " + auth_token}
    request_url = urllib.parse.urljoin(env_var('ASUZ_API_URL'), '/api/SapDataBook/NamePurchaseItems')
    resp = requests.get(url=request_url, headers=headers)
    data = resp.json()
    return data
