"""Data Factory producer import, as published by the APIM infrastructure project."""
import requests

from conf.configuration import secrets, settings


def import_producers(producers):
    config = secrets.get('asset_register', {})
    key = config.get('producer_import_api_key')
    assert key, ('Missing secrets.asset_register.producer_import_api_key; '
                 'POST /idpay-itn/df/producers requires the Data Factory subscription')
    return requests.post(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}/df/producers',
        headers={settings.API_KEY_HEADER: key},
        json={'producers': producers}, timeout=settings.default_timeout,
    )
