import requests

from conf.configuration import settings


def timeline(initiative_id, token):
    """API to get timeline of a user
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.timeline}/{initiative_id}/?page=0&size=10',
        headers={
            "Authorization": f'Bearer {token}',
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
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet}/{initiative_id}',
        headers={
            "Authorization": f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=5000)


def internal_initiative_statistics(organization_id: str, initiative_id: str):
    """API to get initiative statistics.
        :param organization_id: ID of the organization of interest.
        :param initiative_id: ID of the initiative of interest.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.INTERNAL}{settings.IDPAY.endpoints.initiative.microservice_path}{settings.IDPAY.domain}{settings.IDPAY.endpoints.initiative.start_path}/{organization_id}{settings.IDPAY.endpoints.initiative.path}/{initiative_id}{settings.IDPAY.endpoints.initiative.end_path}',
        headers={
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
            "Authorization": f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        json=body,
        timeout=5000)
