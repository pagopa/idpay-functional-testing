import requests

from conf.configuration import secrets
from conf.configuration import settings


def control_mocked_isee(fc: str,
                        isee: float,
                        isee_type: str = 'ORDINARIO'):
    """API control mocked ISEE value for a citizen
        :param fc: Fiscal code of the citizen
        :param isee: Desired ISEE to set for the user
        :param isee_type: Type of ISEE, one of the following:
            - ORDINARIO
            - MINORENNE
            - UNIVERSITARIO
            - SOCIOSANITARIO
            - DOTTORATO
            - RESIDENZIALE
            - CORRENTE
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.post(f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.mock.isee}',
                         headers={
                             'Content-Type': 'application/json',
                             settings.API_KEY_HEADER: secrets.api_key.RTD_Mock_API_Product,
                             'Fiscal-Code': fc,
                         },
                         json={
                             'iseeTypeMap': {
                                 isee_type.upper(): isee
                             }
                         },
                         timeout=settings.default_timeout
                         )


def put_mocked_family(family: list):
    """API to mock a family grouping citizens in one family
        :param family: Fiscal code of the family members
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(
        f'{settings.base_path.IDPAY.internal}/idpaymock{settings.IDPAY.domain}{settings.IDPAY.endpoints.mock.family}',
        headers={
            'Content-Type': 'application/json'
        },
        json=family,
        timeout=settings.default_timeout
    )


def get_family_from_id(family_id: str):
    """API to get user ID of members given family ID
        :param family_id: Family ID of interest
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IDPAY.internal}/idpaymock{settings.IDPAY.domain}{settings.IDPAY.endpoints.mock.family}/user/{family_id}',
        timeout=settings.default_timeout
    )
