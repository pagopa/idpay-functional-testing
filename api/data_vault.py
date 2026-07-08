import requests

from conf.configuration import secrets
from conf.configuration import settings

def data_vault_tokenize(pii:str):
    """API to tokenize
        :param pii
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.mcshared_data_vault.internal_path}',
                        headers={
                            'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'x-api-key': secrets.api_key.MCSHARED_DATA_VAULT
                        },
                        json={
                            'pii': pii
                        },
                        timeout=settings.default_timeout
                        )

def data_vault_detokenize(token):
    """API to detokenize
        :param token: token IO
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.mcshared_data_vault.internal_path}/{token}{settings.IDPAY.endpoints.mcshared_data_vault.detokenize}',
                        headers={
                            'Content-Type': 'application/json',
                            'x-api-key': secrets.api_key.MCSHARED_DATA_VAULT
                        },
                        timeout=settings.default_timeout
                        )