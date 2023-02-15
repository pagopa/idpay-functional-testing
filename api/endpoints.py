import requests

BASE_URL = "https://httpbin.org/"


def get_uuid():
    response = requests.get(f"{BASE_URL}/uuid")
    return response
