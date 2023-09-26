import requests

from conf.configuration import secrets
from conf.configuration import settings


def get_pdv_token(fiscal_code: str):
    """API to get Personal Data Vault token associated to the desired fiscal code.
            :param fiscal_code: Fiscal code of interest.
            :returns: the response of the call.
            :rtype: requests.Response
        """
    return requests.put(
        url=f'{settings.base_path.PDV}{settings.PDV.endpoints.tokenizer}',
        headers={
            'Content-Type': 'application/json',
            'x-api-key': secrets.api_key.PDV
        },
        json={
            'pii': fiscal_code
        },
        timeout=settings.default_timeout
    )


def detokenize_pdv_token(token: str):
    """API to get fiscal code given a Personal Data Vault token.
                :param token: Fiscal code of interest.
                :returns: the response of the call.
                :rtype: requests.Response
            """
    return requests.get(
        url=f'{settings.base_path.PDV}{settings.PDV.endpoints.tokenizer}/{token}/pii',
        headers={
            'Content-Type': 'application/json',
            'x-api-key': secrets.api_key.PDV
        },
        json={
            'pii': token
        },
        timeout=settings.default_timeout
    )
