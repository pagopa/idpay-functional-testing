"""Module containing onboarding endpoint
"""
import requests

from conf.configuration import settings


def accept_terms_and_conditions(token, initiative_id):
    """API to accept terms and conditions
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
                        timeout=settings.default_timeout
                        )


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
        timeout=settings.default_timeout
    )


def pdnd_autocertification(token, initiative_id, pdnd_accept='true', self_declaration_accepted='true'):
    """API to put autocertification
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :param pdnd_accept: citizen's PDND consent
        :param self_declaration_accepted: citizen self-declaration consent
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.consent}',
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {token}',
                        },
                        json={'initiativeId': initiative_id,
                              'pdndAccept': pdnd_accept,
                              'selfDeclarationList': [
                                  {
                                      '_type': 'boolean',
                                      'code': '1',
                                      'accepted': self_declaration_accepted
                                  }]
                              },
                        timeout=settings.default_timeout
                        )


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
        timeout=settings.default_timeout
    )
