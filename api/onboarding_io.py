import requests

from conf.configuration import settings, secrets


def acceptTandC(url, token, initiativeId):
    """API to obtain an IO like token from a stub
        :param url: loginUrl
        :param taxCode: taxCode of the user 
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.put(url,
                        headers={settings['API_KEY_HEADER']: secrets.api_key,
                                 'Content-Type': 'application/json',
                                 "Authorization": f'Bearer {token}',
                                 },
                        json={'initiativeId': initiativeId},
                        timeout=5000)
