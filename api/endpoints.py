"""Endpoint collection
"""
import requests

from conf.configuration import settings

BASE_URL = "https://httpbin.org/"


def get_uuid():
    """API obtain an uuidV4
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    response = requests.get(f"{BASE_URL}/uuid", timeout=5000)
    return response


def get_headers(api_key: str):
    """API obtain an uuidV4
        :param api_key: API key used in the call.
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    response = requests.get(f"{BASE_URL}/headers",
                            headers={settings['API_KEY_HEADER']: api_key},
                            timeout=5000)
    return response
