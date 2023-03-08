"""Module containing issuer APIs
"""
import requests

from conf.configuration import settings, secrets


def enroll(url, tax_code, body):
    """API to enroll a citizen through Issuer API
        :param url: loginUrl
        :param tax_code: taxCode of the user
        :param body: json body containing card info
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    cert = (settings.mauth_paths.cert, settings.mauth_paths.key)
    return requests.put(url,
                        cert=cert,
                        headers={
                            "Ocp-Apim-Subscription-Key": secrets.api_key_issuer,
                            "Accept-Language": "it_IT",
                            "Fiscal-Code": tax_code
                        },
                        json=body,
                        timeout=5000
                        )
