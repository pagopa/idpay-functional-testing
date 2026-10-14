"""Call the email service directly for its HTTP acceptance contract."""
import requests

from conf.configuration import settings
from conf.configuration import secrets


def notify(payload, headers=None):
    url = (f'{secrets.base_path.IO}{settings.IDPAY.domain}'
           f'{settings.IDPAY.endpoints.asset_register.notify_path}')
    return requests.post(url, json=payload, headers=headers or {},
                         timeout=settings.default_timeout, allow_redirects=False)
