import requests

from conf.configuration import settings
from util.certs_loader import load_certificates
from util.dataset_utility import tomorrow_date

default_timeout = 5000
long_timeout = 60000


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
        timeout=default_timeout
    )


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
        timeout=default_timeout)


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
        timeout=default_timeout)


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
        timeout=default_timeout)


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
        timeout=default_timeout)


def get_iban_list(token):
    """API to get list of IBANs associated to a citizen.
        :param token: token IO.
    """
    cert = load_certificates()
    return requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.iban.end_path}',
        cert=cert,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it_IT',
        },
        timeout=default_timeout)


def get_iban_info(iban, token):
    """API to get information about an IBAN enrolled by a citizen.
        :param iban: IBAN of interest.
        :param token: token IO.
    """
    cert = load_certificates()
    return requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.iban.end_path}/{iban}',
        cert=cert,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it_IT',
        },
        timeout=default_timeout)


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
        timeout=default_timeout)


def force_reward():
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.rewards.path}{settings.IDPAY.endpoints.rewards.force_reward}{tomorrow_date()}',
        timeout=long_timeout
    )


def get_reward_content(organization_id, initiative_id, export_id):
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.rewards.path}/organization/{organization_id}/initiative/{initiative_id}/reward/notification/exports/{export_id}/content',
        timeout=default_timeout
    )


def get_initiative_statistics(organization_id, initiative_id):
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.statistics.path}/organization/{organization_id}/initiative/{initiative_id}/statistics',
        timeout=default_timeout
    )
