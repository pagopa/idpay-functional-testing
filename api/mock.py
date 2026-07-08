import json

import requests
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
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.post(f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.mock.internal_path}{settings.IDPAY.endpoints.mock.isee}',
                         headers={
                             'Content-Type': 'application/json',

                             'Fiscal-Code': fc,
                         },
                         json={
                             'iseeTypeMap': {
                                 isee_type.upper(): isee
                             }
                         },
                         timeout=settings.default_timeout
                         )


def put_mocked_family(citizens_cf: list):
    """API to mock a family grouping citizens in one family
        :param citizens_cf: Citizen CF's of the family members
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.mock.internal_path}{settings.IDPAY.endpoints.mock.family}',
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps(citizens_cf),
        timeout=settings.default_timeout
    )


def get_family_from_user_id(user_id: str):
    """API to get family id of members
        :param user_id: user ID of a family member
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.mock.internal_path}{settings.IDPAY.endpoints.mock.family}/user/{user_id}',
        headers={
            'Content-Type': 'application/json'
        },
        timeout=settings.default_timeout
    )
