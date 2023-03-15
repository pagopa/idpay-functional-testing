import os

import requests

from conf.configuration import secrets, settings
from util.certs_loader import load_certificates


def pm_salt():
    """API to obtain the current salt from the payment manager
       :returns:  The response of the call.
       :rtype: requests.Response
    """
    cert = load_certificates()
    response = requests.get(
        f'{settings.base_path.RTD}{settings.RTD.domain}{settings.RTD.endpoints.payment_instrument_manager.path}{settings.RTD.endpoints.payment_instrument_manager.version}{settings.RTD.endpoints.payment_instrument_manager.salt}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.RTD_API_Product,
        }
    )
    return response.text


def public_key():
    """API to obtain RTD public key to encrypt transactions file.
           :returns:  The response of the call.
           :rtype: requests.Response
    """
    cert = load_certificates()
    return requests.get(
        f'{settings.base_path.RTD}{settings.RTD.domain}{settings.RTD.endpoints.transactions.path}{settings.RTD.endpoints.transactions.public_key}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.RTD_API_Product,
            "Content-Type": "application/octet-stream",
        },
        timeout=5000)


def sas_token():
    """API to obtain a SAS token for PGP upload.
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    cert = load_certificates()
    return requests.post(
        f'{settings.base_path.RTD}{settings.RTD.domain}{settings.RTD.endpoints.transactions.path}{settings.RTD.endpoints.transactions.SAS_token}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.RTD_API_Product,
            "Content-Type": "application/octet-stream",
            "x-ms-blob-type": "BlockBlob",
            "x-ms-version": "2021-08-06"
        },
        timeout=5000)


def upload_file(authorized_container, encrypted_file_path, sas):
    """API to obtain an IO like token from a stub
        :param authorized_container: destination container
        :param encrypted_file_path: path to pgp file
        :param sas: current token SAS
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    cert = load_certificates()
    with open(encrypted_file_path, 'rb') as f:
        response = requests.put(
            f'{settings.base_path.RTD}{settings.RTD.endpoints.pagopastorage}/{authorized_container}/{os.path.basename(encrypted_file_path)}?{sas}',
            cert=cert,
            data=f,
            headers={
                settings.API_KEY_HEADER: secrets.api_key.RTD_API_Product,
                "Content-Type": "application/octet-stream",
                "x-ms-blob-type": "BlockBlob",
                "x-ms-version": "2021-08-06"
            },
        )
    return response
