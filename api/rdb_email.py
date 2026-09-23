"""Call the email service directly for its HTTP acceptance contract."""
import requests

from conf.configuration import settings


def notify(url, payload, headers=None):
    return requests.post(url, json=payload, headers=headers or {},
                         timeout=settings.default_timeout, allow_redirects=False)
