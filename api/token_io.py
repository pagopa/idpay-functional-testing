import requests

from conf.configuration import secrets
from conf.configuration import settings


def login(tax_code):
    """API to obtain an IO like token from a stub
        :param tax_code: taxCode of the user
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.post(f'{settings.base_path.IO}{settings.RTD.domain}{settings.RTD.endpoints.mock_io.login}',
                         headers={
                             'Content-Type': 'application/json',
                             settings.API_KEY_HEADER: secrets.api_key.RTD_Mock_API_Product
                         },
                         params={'fiscalCode': tax_code},
                         timeout=settings.default_timeout
                         )


def introspect(token):
    """API to introspect an IO token and get user data
        :param token: IO token to introspect
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(f'{settings.base_path.IO}{settings.RTD.domain}{settings.RTD.endpoints.mock_io.user}',
                        headers={
                            'Content-Type': 'application/json',
                            settings.API_KEY_HEADER: secrets.api_key.RTD_Mock_API_Product
                        },
                        params={
                            'token': token
                        },
                        timeout=settings.default_timeout
                        )
