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
