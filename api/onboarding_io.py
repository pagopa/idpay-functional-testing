"""Module containing onboarding endpoint
"""
import requests

from conf.configuration import secrets
from conf.configuration import settings


def save_onboarding(token, initiative_id, confirmedTos = True, pdnd_accept=True, self_declaration_list=None, user_mail="test@email.com", user_mail_confirmation="test@email.com"):
    """API to save onboarding
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :param confirmedTos: citizen's TOS consent
        :param pdnd_accept: citizen's PDND consent
        :param user_mail: citizen's email
        :param user_mail_confirmation: citizen's email confirmation
        :returns: the response of the call.
        :rtype: requests.Response
    """
    if self_declaration_list is None:
        self_declaration_list = []

    return requests.put(f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.path}',
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {token}',
                        },
                        json={
                                'initiativeId': initiative_id,
                                'confirmedTos': confirmedTos,
                                'pdndAccept': pdnd_accept,
                                'selfDeclarationList': self_declaration_list,
                                'userMail': user_mail,
                                'userMailConfirmation': user_mail_confirmation
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
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.path}/{initiative_id}{settings.IDPAY.endpoints.onboarding.status}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        timeout=settings.default_timeout
    )