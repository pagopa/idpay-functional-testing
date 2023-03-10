"""Module containing onboarding endpoint
"""
import requests


def accept_terms_and_condition(url, token, initiative_id):
    """API to accept terms and condition
        :param url: terms and condition url
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.put(url,
                        headers={
                            'Content-Type': 'application/json',
                            "Authorization": f'Bearer {token}',
                        },
                        json={'initiativeId': initiative_id},
                        timeout=5000)


def check_prerequisites(url, token, initiative_id):
    """API to put check prerequisites
        :param url: check prerequisites url
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.put(url,
                        headers={
                            'Content-Type': 'application/json',
                            "Authorization": f'Bearer {token}',
                        },
                        json={'initiativeId': initiative_id},
                        timeout=5000)


def pdnd_autocertification(url, token, initiative_id):
    """API to put autocertification
        :param url: autocertification url
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.put(url,
                        headers={
                            'Content-Type': 'application/json',
                            "Authorization": f'Bearer {token}',
                        },
                        json={'initiativeId': initiative_id,
                              "pdndAccept": 'true',
                              "selfDeclarationList": [
                                  {
                                      "_type": "boolean",
                                      "code": "1",
                                      "accepted": 'true'
                                  }]
                              },
                        timeout=5000)


def status_onboarding(url, token, initiative_id):
    """API to get onboarding status
        :param url: check url
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.get(url,
                        headers={
                            'Content-Type': 'application/json',
                            "Authorization": f'Bearer {token}',
                        },
                        json={'initiativeId': initiative_id},
                        timeout=5000)
