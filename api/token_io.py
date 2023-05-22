import requests

from conf.configuration import settings


def login(tax_code):
    """API to obtain an IO like token from a stub
        :param tax_code: taxCode of the user
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.post(f'{settings.base_path.IO}{settings.BPD.domain}{settings.BPD.endpoints.login}',
                         headers={
                             'Content-Type': 'application/json', },
                         params={'fiscalCode': tax_code},
                         timeout=settings.default_timeout
                         )


def introspect(token):
    """API to introspect an IOtoken and get user data
        :param token: IO token to introspect
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(f'{settings.base_path.IO}{settings.BPD.domain}{settings.BPD.endpoints.user}',
                        headers={
                            'Content-Type': 'application/json'
                        },
                        params={
                            'token': token
                        },
                        timeout=settings.default_timeout
                        )
