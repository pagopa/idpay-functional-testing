"""Module containing onboarding endpoint
"""
import requests

from conf.configuration import settings


def accept_terms_and_condition(token, initiative_id):
    """API to accept terms and condition
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.path}',
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {token}',
                        },
                        json={'initiativeId': initiative_id},
                        timeout=5000)


def check_prerequisites(token, initiative_id):
    """API to put check prerequisites
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.initiative}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        json={'initiativeId': initiative_id},
        timeout=5000)


def pdnd_autocertification(token, initiative_id):
    """API to put autocertification
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.consent}',
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {token}',
                        },
                        json={'initiativeId': initiative_id,
                              'pdndAccept': 'true',
                              'selfDeclarationList': [
                                  {
                                      '_type': 'boolean',
                                      'code': '1',
                                      'accepted': 'true'
                                  }]
                              },
                        timeout=5000)


def status_onboarding(token, initiative_id):
    """API to get onboarding status
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.path}/{initiative_id}{settings.IDPAY.endpoints.onboarding.status}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        json={'initiativeId': initiative_id},
        timeout=5000)
