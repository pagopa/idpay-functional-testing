import requests

from conf.configuration import settings, secrets


def login(url, taxCode):
    """API to obtain an IO like token from a stub
        :param url: loginUrl
        :param taxCode: taxCode of the user 
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.post(url,
                         headers={settings.API_KEY_HEADER: secrets.api_key,
                                  'Content-Type': 'application/json', },
                         params={'fiscalCode': taxCode},
                         timeout=5000)

def introspect(url, token):
    """API to introspect an IOtoken and get user data
        :param url: loginUrl
        :param taxCode: taxCode of the user 
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.get(url,
                         headers={settings['API_KEY_HEADER']: secrets.api_key,
                                  'Content-Type': 'application/json', },
                         params={'token': token},
                         timeout=5000)
