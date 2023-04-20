import requests

from conf.configuration import settings
from util.certs_loader import load_certificates


def timeline(initiative_id, token, page: int = 1):
    """API to get timeline of a user
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :param page: page to query.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.timeline.path}/{initiative_id}/?page={page}&size=10',
        headers={
            'Authorization': f'Bearer {token}',
        },
        timeout=5000)


def wallet(initiative_id, token):
    """API to get citizen wallet.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=5000)


def unsubscribe(initiative_id, token):
    """API to unsubscribe a citizen from an initiative.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.delete(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}{settings.IDPAY.endpoints.wallet.unsubscribe}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=5000)


def enroll_iban(initiative_id, token, body):
    """API to enroll an IBAN
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :param body: JSON of IBAN and its description.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.iban.start_path}/{initiative_id}{settings.IDPAY.endpoints.onboarding.iban.end_path}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        json=body,
        timeout=5000)


def get_payment_instruments(initiative_id, token):
    """API to get payment instruments.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
    """
    cert = load_certificates()
    return requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}{settings.IDPAY.endpoints.wallet.end_path}',
        cert=cert,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it_IT',
        },
        timeout=5000)


def remove_payment_instrument(initiative_id, token, instrument_id):
    """API to remove payment instrument by instrument ID.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :param instrument_id: ID of the card to remove.
    """
    cert = load_certificates()
    return requests.delete(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}{settings.IDPAY.endpoints.wallet.end_path}/{instrument_id}',
        cert=cert,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it_IT',
        },
        timeout=5000)
