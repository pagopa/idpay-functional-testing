"""Module containing onboarding endpoint
"""
import requests

from conf.configuration import settings


def save_onboarding(token, initiative_id, confirmedTos = True, pdnd_accept=True, self_declaration_list=None, self_declaration_accepted =True):
    """API to accept terms and conditions
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :param confirmedTos: citizen's TOS consent
        :param pdnd_accept: citizen's PDND consent
        :param self_declaration_accepted: citizen self-declaration consent
        :returns: the response of the call.
        :rtype: requests.Response
    """
    if self_declaration_list is None:
        self_declaration_list = [{
            '_type': 'boolean',
            'code': '1',
            'accepted': self_declaration_accepted
        }]

    return requests.put(f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.path}',
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {token}',
                        },
                        json={
                                'initiativeId': initiative_id,
                                'confirmedTos': confirmedTos,
                                'pdndAccept': pdnd_accept,
                                'selfDeclarationList': self_declaration_list,
                                "userMail":"test@email.com",
                                "userMailConfirmation":"test@email.com"
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
        timeout=settings.default_timeout
    )
