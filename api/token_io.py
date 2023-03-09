import requests


def login(url, tax_code):
    """API to obtain an IO like token from a stub
        :param url: loginUrl
        :param tax_code: taxCode of the user
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.post(url,
                         headers={
                             'Content-Type': 'application/json', },
                         params={'fiscalCode': tax_code},
                         timeout=5000)


def introspect(url, token):
    """API to introspect an IOtoken and get user data
        :param url: loginUrl
        :param taxCode: taxCode of the user 
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.get(url,
                        headers={
                            'Content-Type': 'application/json'
                        },
                        params={
                            'token': token
                        },
                        timeout=5000)
