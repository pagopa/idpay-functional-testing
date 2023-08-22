import requests

from conf.configuration import secrets
from conf.configuration import settings


def control_mocked_isee(fc: str,
                        isee: float):
    """API control mocked ISEE value for a citizen
        :param fc: Fiscal code of the citizen
        :param isee: Desired ISEE to set for the user
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
                                 'ORDINARIO': isee
                             }
                         },
                         timeout=settings.default_timeout
                         )
