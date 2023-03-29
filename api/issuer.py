"""Module containing issuer APIs
"""
import requests

from conf.configuration import secrets, settings
from util.certs_loader import load_certificates


def enroll(initiative_id, tax_code, body):
    """API to enroll a citizen through Issuer API
        :param initiative_id: ID of the initiative of interest.
        :param tax_code: taxCode of the user
        :param body: json body containing card info
        :returns: the response of the call.
        :rtype: requests.Response
    """

    cert = load_certificates()
    return requests.put(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.enrollment.start_path}/{initiative_id}{settings.IDPAY.endpoints.onboarding.enrollment.end_path}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_APP_ISSUER_PRODUCT,
            'Accept-Language': 'it_IT',
            'Fiscal-Code': tax_code
        },
        json=body,
        timeout=5000
    )
